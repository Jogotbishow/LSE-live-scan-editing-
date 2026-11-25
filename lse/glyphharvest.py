"""Glyph harvest — the document is its own font.

New technology (Raviraj, 2026-11-24, user: "new technology banao ...
j kono front LSE dekhey hubuhu nokol kortey parey"): LSE reproduces a
scanned document's letterforms EXACTLY without knowing the font name,
without the font file, and without any font-identification service.

How: the document CONTAINS the letterforms. Every character the page
uses is printed right there in the scan. Harvest takes a word's ink
plus its KNOWN text (the old value LSE is about to replace — the user
supplies old -> new, so the text is known, never guessed and never
OCR-read) and cuts the word into its characters. Each character's
bitmap, its top/bottom offset from the word's baseline, and its
advance (width + the gap that followed it) are stored in a library
keyed by character. Compose pastes the document's own glyph bitmaps
side by side to render a new string — the letterforms are the
original's own ink, so widths, stems, serifs and spacing match by
construction, not by approximation.

Rules:
- No OCR anywhere: the text of every harvested word is supplied by
  the caller (the edit context). A glyph is never assigned a
  character the caller did not name.
- No font file, no font name, no identification service. A missing
  character (one that never appears on the page, e.g. lowercase 'x'
  on the Raviraj page) is reported as missing, never invented and
  never silently replaced by a look-alike font glyph — the caller
  decides the fallback (usually the font render for that one cell).
- Bitmaps are used at the page's own DPI, at natural size. No
  resampling, no horizontal squeeze, no shrink-to-fit: the composed
  layer is pasted exactly as harvested.
- Bold and regular are kept apart: a glyph variant remembers whether
  its source word was bold, and compose() prefers the matching
  weight. A bold invoice '2' and a regular table '2' are different
  glyphs and must never be mixed.
"""

import base64
import io
import json

import cv2
import numpy as np
from PIL import Image

INK_THRESHOLD = 150  # scan ink: dark core of the printed glyph
# A gap wider than this multiple of the median inter-glyph gap is a
# word space, not letter spacing.
SPACE_GAP_FACTOR = 1.8
# A component wider than this multiple of the median glyph width is
# treated as two touching letters and split at its lightest column.
WIDE_SPLIT_FACTOR = 1.6
# Components smaller than this area (px) are scan specks, not glyphs.
# Components smaller than this area (px) are only trusted when they sit
# ON the baseline band (a '.' has area ~26; a scan speck above the
# line has area ~21 — area alone cannot tell them apart, but the
# baseline can: the dot's bottom IS the baseline, the speck's is
# ~35 px above it).
MIN_GLYPH_AREA = 12
SMALL_GLYPH_AREA = 30
BASELINE_TOLERANCE_PX = 8


def _components(binary):
    """Connected components of a boolean ink array.

    Returns a list of dicts {x, y, w, h, area, mask} in x order.
    """
    n, _lab, stats, _cent = cv2.connectedComponentsWithStats(
        binary.astype(np.uint8), 8)
    comps = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if area < MIN_GLYPH_AREA:
            continue
        comps.append({"x": x, "y": y, "w": w, "h": h, "area": area,
                      "mask": (_lab[y:y + h, x:x + w] == i)})
    comps.sort(key=lambda c: (c["x"], c["y"]))
    return comps


def _merge_dotted(comps):
    """Merge stacked parts of one character ('i' dot + stem, 'j', ':').

    Two components merge when their x-intervals overlap by at least
    half of the narrower one's width and one sits above the other
    (no vertical overlap). The merged glyph keeps the union bitmap.
    """
    merged = []
    used = [False] * len(comps)
    for i, a in enumerate(comps):
        if used[i]:
            continue
        cur = dict(a)
        cur["mask"] = a["mask"].copy()
        for j, b in enumerate(comps):
            if j <= i or used[j]:
                continue
            ox = min(cur["x"] + cur["w"], b["x"] + b["w"]) - max(cur["x"], b["x"])
            if ox <= 0:
                continue
            narrow = min(cur["w"], b["w"])
            vertical_gap = (b["y"] >= cur["y"] + cur["h"]) or \
                (cur["y"] >= b["y"] + b["h"])
            if ox >= 0.5 * narrow and vertical_gap:
                x0 = min(cur["x"], b["x"])
                y0 = min(cur["y"], b["y"])
                x1 = max(cur["x"] + cur["w"], b["x"] + b["w"])
                y1 = max(cur["y"] + cur["h"], b["y"] + b["h"])
                mask = np.zeros((y1 - y0, x1 - x0), dtype=bool)
                mask[cur["y"] - y0:cur["y"] - y0 + cur["h"],
                     cur["x"] - x0:cur["x"] - x0 + cur["w"]] |= cur["mask"]
                mask[b["y"] - y0:b["y"] - y0 + b["h"],
                     b["x"] - x0:b["x"] - x0 + b["w"]] |= b["mask"]
                cur = {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0,
                       "area": int(mask.sum()), "mask": mask}
                used[j] = True
        merged.append(cur)
        used[i] = True
    merged.sort(key=lambda c: (c["x"], c["y"]))
    return merged


def _split_wide(comps):
    """Split a too-wide component into two letters — but ONLY when
    it is really two letters joined by a narrow bridge. A single
    wide letter defeats every naive test: the 'U' bottom curve is
    2 px thick over five columns (an "empty run"), and the 'm' arch
    gaps are empty columns with tall stems beside them. So the cut
    needs ALL THREE of: (a) the cut column itself nearly empty
    (<= 3 dark px); (b) the columns 4 px to either side TALL
    (>= half the component height — the two letters' bodies); (c)
    the cut at least 0.8 x median width from BOTH edges (an 'm'
    arch gap sits ~13 px in; a real letter boundary sits a full
    letter width in). A component that fails any of the three stays
    whole — the harvest then reports a mismatch LOUDLY instead of
    inventing a character by cutting a 'U' or an 'm' in half.
    Returns (components, split count)."""
    if not comps:
        return comps, 0
    widths = sorted(c["w"] for c in comps)
    med = widths[len(widths) // 2]
    out = []
    splits = 0
    for c in comps:
        if c["w"] <= WIDE_SPLIT_FACTOR * med:
            out.append(c)
            continue
        x, y, w, h = c["x"], c["y"], c["w"], c["h"]
        col_ink = c["mask"].sum(axis=0)
        lo = int(w * 0.25)
        hi = int(w * 0.75)
        cut = lo + int(np.argmin(col_ink[lo:hi + 1]))
        ok = (col_ink[cut] <= 3
              and col_ink[max(0, cut - 4)] >= 0.5 * h
              and col_ink[min(w - 1, cut + 4)] >= 0.5 * h
              and cut >= 0.8 * med
              and (w - cut) >= 0.8 * med)
        if not ok:
            out.append(c)
            continue
        left = {"x": x, "y": y, "w": cut, "h": h,
                "area": int(c["mask"][:, :cut].sum()),
                "mask": c["mask"][:, :cut].copy()}
        right = {"x": x + cut, "y": y, "w": w - cut, "h": h,
                 "area": int(c["mask"][:, cut:].sum()),
                 "mask": c["mask"][:, cut:].copy()}
        out.extend([left, right])
        splits += 1
    out.sort(key=lambda c: (c["x"], c["y"]))
    return out, splits


def segment_word(gray, box, threshold=INK_THRESHOLD):
    """Cut one word's ink into glyphs, left to right.

    ``gray`` is the page grayscale (numpy, [y, x]); ``box`` is the
    word's tight ink box [x0, y0, x1, y1] in the same coordinates.
    Returns a list of glyph records; a record is either a glyph
    {char: None, bitmap, x0, top_rel, bottom_rel, w, h, gap_after,
    advance} or a space {char: ' ', width}. ``top_rel``/``bottom_rel``
    are measured from the word's baseline (the max glyph bottom):
    0 for a baseline-sitter, negative for a raised glyph ('.').
    ``gap_after`` is the gap to the next glyph in the source word.
    """
    x0, y0, x1, y1 = (int(v) for v in box)
    sub = gray[y0:y1, x0:x1]
    binary = sub < threshold
    comps = _components(binary)
    comps = _merge_dotted(comps)
    comps, splits = _split_wide(comps)
    if not comps:
        return [], {"splits": splits, "baseline": None}
    # Baseline from the solid glyphs; a small component only counts
    # as a glyph when it sits on that baseline (a '.' does; a scan
    # speck floating above the line does not).
    big = [c for c in comps if c["area"] >= SMALL_GLYPH_AREA]
    base = max(c["y"] + c["h"] for c in big) if big else \
        max(c["y"] + c["h"] for c in comps)
    comps = [c for c in comps
             if c["area"] >= SMALL_GLYPH_AREA
             or abs((c["y"] + c["h"]) - base) <= BASELINE_TOLERANCE_PX]
    if not comps:
        return [], {"splits": splits, "baseline": None}
    baseline = base
    gaps = []
    for a, b in zip(comps, comps[1:]):
        gaps.append(b["x"] - (a["x"] + a["w"]))
    # Two gap kinds, and they are NOT interchangeable (fin10):
    # the gap before a '.' is the dot's wide side bearing (~12 px),
    # the gap before a letter is ~5 px. A glyph harvested from
    # before a dot ("53.32"'s '3', "74.75"'s '4') carries the
    # dot-gap; composing it before a letter ("PLNU1073700249"'s
    # '3' before '7') then spaces it 7 px too wide — the fin10
    # batch came out 10 px wide that way. Conversely a dot-gap
    # must be KEPT when the glyph really is followed by a '.'
    # (the invoice's "07.08.2026" dots sit 12 px after the digit).
    # So each glyph records both: gap_after (to a following
    # letter) and gap_after_dot (to a following '.').
    def _is_small(c):
        return c["area"] < SMALL_GLYPH_AREA
    # The median letter gap must exclude BOTH the dot-gaps (wide
    # side bearings) and the space-gaps (a real word space): a
    # word that is mostly spaces would otherwise median to 21 px.
    raw_med = float(np.median(gaps)) if gaps else 0.0
    letter_gaps = [gaps[i] for i in range(len(gaps))
                   if not _is_small(comps[i + 1])
                   and gaps[i] <= SPACE_GAP_FACTOR * max(raw_med, 1.0)]
    dot_gaps = [gaps[i] for i in range(len(gaps))
                if _is_small(comps[i + 1])]
    med_gap = float(np.median(letter_gaps)) if letter_gaps \
        else float(np.median(gaps)) if gaps else 0.0
    med_dot_gap = float(np.median(dot_gaps)) if dot_gaps else med_gap
    med_h = float(np.median([c["h"] for c in comps])) if comps else 0.0
    glyphs = []
    for i, c in enumerate(comps):
        if i < len(gaps):
            if _is_small(comps[i + 1]):
                gap_after, gap_after_dot = med_gap, float(gaps[i])
            else:
                gap_after, gap_after_dot = float(gaps[i]), med_dot_gap
        else:
            gap_after, gap_after_dot = med_gap, med_dot_gap
        glyphs.append({
            "char": None,
            "bitmap": c["mask"],
            "x0": c["x"],
            "top_rel": c["y"] - baseline,
            "bottom_rel": (c["y"] + c["h"]) - baseline,
            "w": c["w"], "h": c["h"],
            "gap_after": float(gap_after),
            "gap_after_dot": float(gap_after_dot),
            "advance": c["w"] + float(gap_after),
        })
        # A word space is a gap that is BOTH wide relative to the
        # letter gaps AND wide in absolute terms (a real space is
        # ~0.5 x cap height; the gap beside a '.' is ~0.2 x).
        if i < len(gaps) and gaps[i] > SPACE_GAP_FACTOR * max(med_gap, 1.0) \
                and gaps[i] > 0.35 * med_h:
            glyphs.append({"char": " ", "width": float(gaps[i]),
                           "gap_after": 0.0, "advance": float(gaps[i])})
            # The space gap belongs to the SPACE item, not to the
            # glyph before it: a glyph harvested from before a space
            # ("HSL"'s 'L', gap 21) would otherwise carry a 21 px
            # gap into any new string it is composed into (fin10:
            # the batch's 'L' sat 14 px too far from 'N' because
            # the picked 'L' came from "HSL "). The glyph keeps
            # the median letter gap; the space item keeps the width.
            glyphs[-2]["gap_after"] = med_gap
            glyphs[-2]["advance"] = glyphs[-2]["w"] + med_gap
    return glyphs, {"splits": splits, "baseline": baseline,
                    "median_gap": med_gap}


class GlyphLibrary:
    """A document's own glyphs, keyed by character."""

    def __init__(self):
        # char -> list of variants; each variant is a glyph record
        # plus "bold" (whether its source word was bold).
        self.glyphs = {}
        self.space_width = None
        self.words_harvested = 0
        self.splits = 0
        self._gaps = []

    def add(self, gray, box, text, bold=False):
        """Harvest one word. ``text`` is the word's KNOWN text (from
        the edit context, never OCR). Returns a report dict."""
        glyphs, info = segment_word(gray, box)
        self.splits += info["splits"]
        chars = [g for g in glyphs if g["char"] is None]
        spaces = [g for g in glyphs if g["char"] == " "]
        expected = [ch for ch in text if ch != " "]
        report = {"text": text, "bold": bold,
                  "components": len(chars), "chars": len(expected),
                  "spaces_found": len(spaces),
                  "spaces_expected": text.count(" "),
                  "splits": info["splits"], "added": [], "mismatch": None}
        if len(chars) != len(expected):
            report["mismatch"] = (
                f"{len(chars)} glyph components for {len(expected)} "
                f"characters in {text!r}")
            return report
        if self.space_width is None and spaces:
            self.space_width = spaces[0]["width"]
        gi = 0
        for ch in expected:
            g = chars[gi]
            gi += 1
            rec = dict(g)
            rec["char"] = ch
            rec["bold"] = bold
            # Which word this glyph came from: composing a new
            # value for a cell should prefer that cell's own old
            # word's glyphs (same letters, same context, same
            # side bearings) over the first variant in the library.
            rec["source"] = text
            self.glyphs.setdefault(ch, []).append(rec)
            self._gaps.append(g["gap_after"])
            report["added"].append(ch)
        self.words_harvested += 1
        return report

    def median_gap(self):
        """The document's own median inter-letter gap (px) — the
        spacing a retouched glyph is placed with."""
        return float(np.median(self._gaps)) if self._gaps else 7.0

    def retouched_chars(self, text):
        """Characters of ``text`` that would render from retouched
        (not harvested) glyphs."""
        out = []
        for ch in text:
            if ch == " ":
                continue
            vs = self.glyphs.get(ch, [])
            if vs and all(v.get("retouched") for v in vs):
                out.append(ch)
        return sorted(set(out))

    def missing(self, text):
        """Characters of ``text`` the library cannot render."""
        return sorted({ch for ch in text
                       if ch != " " and ch not in self.glyphs})

    def cap_height(self):
        """Median height of the cap/digit glyphs (the library's cap
        height in px)."""
        hs = [g["h"] for ch, vs in self.glyphs.items()
              for g in vs if ch.isupper() or ch.isdigit()]
        return float(np.median(hs)) if hs else 0.0

    def _pick(self, ch, bold, prefer_source=None):
        variants = self.glyphs.get(ch, [])
        # Harvested ink first (the document's own glyphs); retouched
        # only when no harvested variant exists.
        harvested = [v for v in variants if not v.get("retouched")]
        pool = harvested if harvested else variants
        # Prefer a glyph from the word being replaced: its side
        # bearings are that word's own (the batch's 'L' sits 6 px
        # from 'N'; the spec's "HSL" 'L' sits 21 px from a space).
        if prefer_source is not None:
            for v in pool:
                if v["bold"] == bold and v.get("source") == prefer_source:
                    return v
        for v in pool:
            if v["bold"] == bold:
                return v
        return pool[0] if pool else None

    def compose(self, text, bold=False, ink=(0, 0, 0),
                prefer_source=None):
        """Render ``text`` from the document's own glyphs.

        ``prefer_source`` is the old word being replaced (its text):
        glyphs harvested from that word are preferred, so a new
        value for a cell is set in that cell's own letterforms and
        spacing. Returns (layer, metrics): layer is an RGBA PIL image
        (transparent background, ink with alpha) in the same
        contract as writeback.render_word_layer; metrics holds
        width, cap height, per-letter widths/gaps and the source of
        every glyph. Raises KeyError listing the missing characters
        (never invents a glyph)."""
        miss = self.missing(text)
        if miss:
            raise KeyError(f"glyph harvest: characters not on the page: "
                           f"{''.join(miss)!r} (in {text!r})")
        space_w = self.space_width if self.space_width is not None else 10.0
        items = []
        for ch in text:
            if ch == " ":
                items.append({"char": " ", "w": space_w, "advance": space_w,
                              "top_rel": 0, "bottom_rel": 0, "bitmap": None})
            else:
                items.append(self._pick(ch, bold, prefer_source))
        with_ink = [it for it in items if it["bitmap"] is not None]
        baseline_y = max(-it["top_rel"] for it in with_ink) if with_ink else 0
        # A glyph's bottom may sit a pixel below the word baseline
        # (the '.' of a synthetic render ends 1 px under the caps'
        # baseline); the canvas must cover the lowest bottom, not
        # just the tallest top.
        lowest = max([it["bottom_rel"] for it in with_ink] or [0])
        # Place first into a generously sized array, then crop to the
        # tight ink bbox: per-glyph rounding must never overflow it.
        # Effective advances: a glyph's stored advance already
        # includes the gap to the next glyph — and when the next
        # glyph is a word space, that gap IS the space. Counting the
        # space item's width on top would double-count every space
        # (the first fin10 draft rendered the spec 123 px too wide
        # that way). So a glyph before a space advances by its width
        # alone; the space item carries the spacing. And the gap
        # is pair-specific: a glyph followed by a '.' takes its
        # dot-gap (wide side bearing), followed by a letter its
        # letter-gap — the two differ by ~7 px on this page.
        eff = []
        for idx, it in enumerate(items):
            if it["bitmap"] is None:
                eff.append(float(it["advance"]))
            elif idx + 1 < len(items) and items[idx + 1]["bitmap"] is None:
                eff.append(float(it["w"]))
            elif idx + 1 < len(items) and items[idx + 1]["char"] == ".":
                eff.append(float(it["w"]) + float(it.get("gap_after_dot",
                                                       it["gap_after"])))
            else:
                eff.append(float(it["advance"]))
        total_w = int(round(sum(eff) - (eff[-1] - items[-1]["w"])
                            if items else 0))
        height = int(baseline_y + max(0, lowest))
        layer_w = max(1, total_w + 8)
        layer_h = max(1, height + 8)
        arr = np.zeros((layer_h, layer_w, 4), dtype=np.uint8)
        arr[:, :, 0:3] = ink
        x = 0
        letters = []
        for idx, it in enumerate(items):
            if it["bitmap"] is None:
                x += int(round(eff[idx]))
                continue
            y = int(baseline_y + it["top_rel"])
            h, w = it["bitmap"].shape
            arr[y:y + h, x:x + w, 3] = np.where(
                it["bitmap"], 255, arr[y:y + h, x:x + w, 3]).astype(np.uint8)
            letters.append({"char": it["char"], "x": x, "w": w,
                            "gap_after": (eff[idx] - w if idx + 1 < len(items)
                                          else it["gap_after"]),
                            "retouched": bool(it.get("retouched"))})
            x += int(round(eff[idx]))
        alpha = arr[:, :, 3]
        ys, xs = np.where(alpha > 10)
        if len(xs) == 0:
            layer = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            ink_bbox = None
        else:
            ink_bbox = (int(xs.min()), int(ys.min()),
                        int(xs.max()) + 1, int(ys.max()) + 1)
            # Letter x positions are relative to the returned (cropped)
            # layer, not the placement array.
            for l in letters:
                l["x"] -= ink_bbox[0]
            layer = Image.fromarray(
                arr[ink_bbox[1]:ink_bbox[3], ink_bbox[0]:ink_bbox[2]], "RGBA")
        metrics = {"text": text, "bold": bold, "width_px": total_w,
                   "height_px": height, "cap_h_px": self.cap_height(),
                   "ink_bbox": ink_bbox, "letters": letters,
                   "glyphs_from": "document-harvest"}
        return layer, metrics

    def save(self, path):
        """Save the library: one atlas PNG + one JSON manifest."""
        entries = {}
        atlas_rows = []
        y = 0
        for ch, variants in sorted(self.glyphs.items()):
            for vi, v in enumerate(variants):
                key = f"{ch}|{vi}|{'b' if v['bold'] else 'r'}"
                h, w = v["bitmap"].shape
                atlas_rows.append((key, v["bitmap"], y, h, w))
                entries[key] = {"char": ch, "variant": vi,
                                "bold": v["bold"], "x": 0, "y": y,
                                "w": w, "h": h,
                                "top_rel": v["top_rel"],
                                "bottom_rel": v["bottom_rel"],
                                "gap_after": v["gap_after"],
                                "gap_after_dot": v.get("gap_after_dot",
                                                     v["gap_after"]),
                                "advance": v["advance"],
                                "source": v.get("source")}
                y += h + 2
        atlas_w = max((w for _, _, _, _, w in atlas_rows), default=1)
        atlas = np.full((max(1, y), atlas_w), 255, dtype=np.uint8)
        for key, bitmap, yy, h, w in atlas_rows:
            atlas[yy:yy + h, 0:w] = np.where(bitmap, 0, 255).astype(np.uint8)
        Image.fromarray(atlas).save(path + ".atlas.png")
        manifest = {"space_width": self.space_width,
                    "words_harvested": self.words_harvested,
                    "splits": self.splits,
                    "cap_h_px": self.cap_height(),
                    "entries": entries}
        with open(path + ".json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1)
        return path + ".json"

    @classmethod
    def load(cls, path):
        """Load a library saved by save()."""
        with open(path + ".json", encoding="utf-8") as f:
            manifest = json.load(f)
        atlas = np.array(Image.open(path + ".atlas.png").convert("L")) < 150
        lib = cls()
        lib.space_width = manifest["space_width"]
        lib.words_harvested = manifest["words_harvested"]
        lib.splits = manifest["splits"]
        for key, e in manifest["entries"].items():
            bitmap = atlas[e["y"]:e["y"] + e["h"], e["x"]:e["x"] + e["w"]]
            rec = {"char": e["char"], "bitmap": bitmap.copy(),
                   "x0": 0, "top_rel": e["top_rel"],
                   "bottom_rel": e["bottom_rel"], "w": e["w"], "h": e["h"],
                   "gap_after": e["gap_after"],
                   "gap_after_dot": e.get("gap_after_dot", e["gap_after"]),
                   "advance": e["advance"],
                   "source": e.get("source"),
                   "bold": e["bold"]}
            lib.glyphs.setdefault(e["char"], []).append(rec)
        return lib
