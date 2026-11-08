"""Live-page builder — the scan as the page, text as a living layer.

Ports the merged native-300-DPI builder (scan-paper/build_page300.py,
v8) into functions. The HTML template is the v7 template, extracted
verbatim (lse/templates/live_page.html — same extraction build_page300
does at runtime, including its literal ``\\n`` sequences inside JS
strings). Per-word style is measured from pixels, never guessed:

  * stroke ratio: 2 x mean(distance-transform of ink) / height —
    the bold signal (see bold modes below);
  * ink colour: median RGB of the word's ink pixels, with a page-median
    fallback for faint words;
  * cap height: the word's own ink height when cap-like, else the
    line's cap height (skew-corrected coordinates); font size =
    cap_h / 0.70 (the Document DNA clone's cap ratio);
  * heading flip: H1 (grey highlight bar) / H2 (table-header) lines
    from heading.py are forced bold.

BOLD — accepted design (R18 Track C, see DECISIONS.md):
  * "canonical" (default, PG-verified): page-median stroke ratio x
    1.15 + heading flip. This is exactly the merged builder's rule —
    the rule the verified 43/43 fontfix pages were built with.
  * "anchor" (PG-only): the caller supplies a KNOWN-REGULAR word box
    (on PG formats: the Lot value word). Threshold = anchor ratio x
    1.15 + heading flip. R18's measured Lot-anchor hold margin (0.036)
    is recorded as LOT_ANCHOR_HOLD and reported as a diagnostic.
  * "none" (new templates without an anchor): NO automatic bold
    detection at all — bold comes only from heading-flip lines
    (template-marked headings). This is the R18 rule for new templates.

Confidence tiers ("confident" / "check" / "unsure") come from the
prototype's DBNet cross-check validator (improve/round2/conf.py),
which needs per-template validator data and is NOT ported here: the
default tier is "check" unless the caller supplies tiers. The tier
only drives the confidence overlay in the page UI.
"""
import base64
import hashlib
import io
import json
import math
import os
from collections import defaultdict

import cv2
import numpy as np
from PIL import Image

from .heading import heading_lines_guarded as heading_lines

CAP_RATIO = 0.70
BOLD_FACTOR = 1.15
LOT_ANCHOR_HOLD = 0.036  # R18 Track C: measured hold margin of the PG Lot
# anchor (known-regular Lot value word) below the bold line. Recorded
# for diagnostics; the anchor threshold itself uses BOLD_FACTOR, the
# same factor as the canonical rule.
S = 1 / 3  # display scale: 2483/3 = 827 px wide, same as the v7 pages
PAGE_CAPH_FALLBACK = 28.0

LIB_SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
LIB_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def _template():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "templates", "live_page.html")
    with open(path) as f:
        return f.read()


def _to_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(max(0, min(255, v)))) for v in rgb)


def _overlaps_stamp(box, stamps):
    return any(not (box[2] < r[0] or box[0] > r[2] or box[3] < r[1] or box[1] > r[3])
               for r in [s["box"] for s in stamps])


def word_styles(gray, color, seg_words, skew_deg=0.0, bold_mode="canonical",
                anchor_box=None, stamps=None, confidences=None,
                exemplar=None):
    """Measure per-word live-page style from pixels.

    ``seg_words``: seg-dict "words" ([{"box", "line", ...}]).
    ``skew_deg``: the page's deskew correction angle (for cap-height
    classification on skew-corrected coordinates).
    Returns (words, info) where words carry x/y/w/h/fs/bold/color/pb/
    conf/stamp/ratio/cap_h/cls/heading, and info reports the page
    medians, bold threshold, heading lines and flips.
    """
    stamps = stamps or []
    otsu_t, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if otsu_t <= 0:  # pure 1-bit image -> Otsu 0 (M1-class fix)
        otsu_t = 128
    ink = (gray < otsu_t).astype(np.uint8)
    raw = []
    slope = math.tan(math.radians(skew_deg))
    for wd in seg_words:
        x0, y0, x1, y1 = wd["box"]
        h, w = y1 - y0, x1 - x0
        roi = ink[y0:y1, x0:x1]
        n_ink = int(roi.sum()) if roi.size else 0
        ratio = None
        if h >= 12 and n_ink >= 11 and n_ink < roi.size:
            dist = cv2.distanceTransform(roi, cv2.DIST_L2, 3)
            ratio = 2.0 * float(dist[roi > 0].mean()) / h
        rgb = None
        if n_ink >= 5:
            m = color[y0:y1, x0:x1][roi > 0].mean(axis=0)
            rgb = [round(float(v), 1) for v in m[::-1]]
        ys, xs = np.where(roi > 0)
        if len(ys):
            xc = (x0 + x1) / 2
            ink_h = int(ys.max() - ys.min() + 1)
            top_c = int(y0 + ys.min()) - xc * slope
            bot_c = int(y0 + ys.max()) - xc * slope
        else:
            ink_h, top_c, bot_c = 0, None, None
        raw.append({"box": wd["box"], "line": wd.get("line"), "h": h, "w": w,
                    "ratio": ratio, "rgb": rgb, "n_ink": n_ink,
                    "ink_h": ink_h, "top_c": top_c, "bot_c": bot_c})

    ratios = [r["ratio"] for r in raw if r["ratio"] is not None]
    med_ratio = float(np.median(ratios)) if ratios else 0.0
    anchor_ratio = None
    if bold_mode == "anchor":
        if anchor_box is None:
            raise ValueError("bold_mode='anchor' needs anchor_box "
                             "(a known-regular word box, e.g. the Lot value)")
        anchor_ratio = next((r["ratio"] for r in raw
                             if r["box"] == list(anchor_box)
                             and r["ratio"] is not None), None)
        if anchor_ratio is None:
            raise ValueError(f"anchor_box {anchor_box} not found among "
                             f"segmented words (or has no stroke ratio)")
        bold_thr = BOLD_FACTOR * anchor_ratio
    elif bold_mode == "none":
        bold_thr = float("inf")  # no automatic bold detection
    elif bold_mode == "canonical":
        bold_thr = BOLD_FACTOR * med_ratio
    else:
        raise ValueError(f"unknown bold_mode {bold_mode!r}")
    rgbs = np.array([r["rgb"] for r in raw if r["rgb"]], dtype=float)
    page_rgb = [round(float(v), 1) for v in np.median(rgbs, axis=0)] if len(rgbs) else [0, 0, 0]

    lines = defaultdict(list)
    for r in raw:
        lines[r["line"]].append(r)
    line_base = {}
    for ln, rs in lines.items():
        ys = [r["box"][3] for r in rs if r["h"] >= 12] or [r["box"][3] for r in rs]
        line_base[ln] = float(np.median(ys))

    line_captop, line_basec, line_caph = {}, {}, {}
    for ln, rs in lines.items():
        tops = [r["top_c"] for r in rs if r["top_c"] is not None]
        bots = [r["bot_c"] for r in rs if r["bot_c"] is not None]
        captop = float(np.median(tops)) if tops else 0.0
        basec = float(np.median(bots)) if bots else 0.0
        capws = [r for r in rs if r["top_c"] is not None
                 and abs(r["top_c"] - captop) <= 3 and abs(r["bot_c"] - basec) <= 3]
        line_captop[ln] = captop
        line_basec[ln] = basec
        line_caph[ln] = float(np.median([r["ink_h"] for r in capws])) if capws else None
    page_caphs = [v for v in line_caph.values() if v]
    page_caph = float(np.median(page_caphs)) if page_caphs else PAGE_CAPH_FALLBACK

    hd = heading_lines(gray, otsu_t, lines, exemplar=exemplar)
    h1, h2 = hd["h1"], hd["h2"]

    if confidences is None:
        confidences = ["check"] * len(raw)
    if len(confidences) != len(raw):
        raise ValueError(f"confidences length {len(confidences)} != words {len(raw)}")

    words = []
    heading_flips = []
    n_fallback_colour = 0
    for r, conf in zip(raw, confidences):
        x0, y0, x1, y1 = r["box"]
        bold = bool(r["ratio"] is not None and r["ratio"] > bold_thr and r["w"] >= 9)
        hd_reason = None
        if r["line"] in h1:
            hd_reason = "H1"
        elif r["line"] == h2:
            hd_reason = "H2"
        if hd_reason and not bold:
            heading_flips.append({"box": r["box"], "line": r["line"],
                                  "reason": hd_reason, "ratio": r["ratio"]})
        if hd_reason:
            bold = True
        rgb = r["rgb"]
        if r["n_ink"] < 45 or rgb is None or sum(rgb) / 3 > 170:
            rgb = page_rgb
            n_fallback_colour += 1
        pad_img = max(0.0, y1 - line_base[r["line"]])
        if r["top_c"] is not None:
            captop = line_captop[r["line"]]
            basec = line_basec[r["line"]]
            lcaph = line_caph[r["line"]] or page_caph
            has_desc = r["bot_c"] > basec + 3
            is_x = r["top_c"] > captop + 3
            is_over = r["top_c"] < captop - 3
            if has_desc:
                cls, caph = "desc", lcaph
            elif is_x:
                cls, caph = "x-only", lcaph
            elif is_over:
                cls, caph = "overshoot", lcaph
            else:
                cls, caph = "cap", float(r["ink_h"])
        else:
            cls, caph = "empty", page_caph
        fs = round(caph / CAP_RATIO, 1)
        words.append({"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0,
                      "fs": fs, "bold": bold, "color": _to_hex(rgb),
                      "pb": round(pad_img * S, 1), "conf": conf,
                      "stamp": bool(_overlaps_stamp([x0, y0, x1, y1], stamps)),
                      "ratio": round(r["ratio"], 3) if r["ratio"] is not None else None,
                      "cap_h": caph, "cls": cls, "heading": hd_reason})
    info = {"otsu": otsu_t, "median_ratio": round(med_ratio, 4),
            "bold_thr": round(bold_thr, 4) if bold_thr != float("inf") else None,
            "bold_mode": bold_mode, "anchor_ratio": anchor_ratio,
            "anchor_hold": LOT_ANCHOR_HOLD if bold_mode == "anchor" else None,
            "page_rgb": page_rgb, "page_cap_h": page_caph,
            "colour_fallbacks": n_fallback_colour,
            "h1_lines": sorted(h1), "h2_line": h2,
            "heading": {"top_rule": hd["top_rule"], "rule_thr": hd["rule_thr"],
                        "page_max_run": hd["page_max_run"]},
            "heading_flips": heading_flips,
            "n_bold": sum(1 for w in words if w["bold"]),
            "n_stamp": sum(1 for w in words if w["stamp"])}
    return words, info


def _nearest(words, cx, cy):
    best, bd = None, 1e9
    for wd in words:
        ccx = wd["x"] + wd["w"] / 2
        ccy = wd["y"] + wd["h"] / 2
        d = (ccx - cx) ** 2 + (ccy - cy) ** 2
        if d < bd:
            bd, best = d, wd
    return best


def jpeg_b64(image, q=88):
    """Encode a PIL/numpy image as a JPEG data URI.

    q=88, NOT q95 — measured 2026-11-06: the q95 clean is 2,380,472
    base64 chars and Chromium's setProperty SILENTLY DROPS a CSS custom
    property that long (1.8M chars stores fine, 2.38M stores 0), so the
    clean layer was empty and typed text doubled over the original ink.
    q88 is ~1.37M base64 chars, which stores fine.
    """
    if isinstance(image, (str, os.PathLike)):
        image = Image.open(image)
    elif not isinstance(image, Image.Image):
        image = Image.fromarray(np.asarray(image))
    buf = io.BytesIO()
    image.convert("RGB").save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def png_b64(path_or_bytes):
    if isinstance(path_or_bytes, (bytes, bytearray)):
        raw = bytes(path_or_bytes)
    else:
        raw = open(path_or_bytes, "rb").read()
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def _font_b64(path, fallback):
    """Base64 of a TTF (DNA clone when available, else the fallback)."""
    use = path if path and os.path.exists(path) else fallback
    with open(use, "rb") as f:
        return base64.b64encode(f.read()).decode(), os.path.basename(use)


def build_live_page(gray, color, seg, orig_b64, clean_b64, manual_b64,
                    page_meta, out_path, skew_deg=0.0, bold_mode="canonical",
                    anchor_box=None, stamps=None, confidences=None,
                    exemplar=None, dna_regular=None, dna_bold=None,
                    shortlist=None, demo=None):
    """Build one live page HTML file.

    ``gray``/``color``: the native-DPI page render (numpy). ``seg``: the
    seg dict from segment_array(). ``orig_b64``: data URI of the ORIGINAL
    scan bytes (JPEG verbatim / lossless PNG decode — never re-encoded
    JPEG). ``clean_b64``/``manual_b64``: data URIs of the inpainted clean
    layers. ``page_meta``: {page_key, page_no, source_page,
    source_document, item, page_label, old_lot, old_width}.
    ``demo`` (optional): {"lot": {"center": (x, y), "new": str,
    "expected_box": [...]}, "width": {...}} — demo targets are found by
    nearest() and VERIFIED against the expected identity boxes (row
    label + box), never by position alone.
    Returns (html_path, words, info).
    """
    H, W = gray.shape
    words, info = word_styles(gray, color, seg["words"], skew_deg=skew_deg,
                               bold_mode=bold_mode, anchor_box=anchor_box,
                               stamps=stamps, confidences=confidences,
                               exemplar=exemplar)
    demo_json = {"lot": None, "width": None}
    if demo:
        for key in ("lot", "width"):
            if key not in demo:
                continue
            tgt = _nearest(words, *demo[key]["center"])
            box = [tgt["x"], tgt["y"], tgt["x"] + tgt["w"], tgt["y"] + tgt["h"]]
            if demo[key].get("expected_box") is not None:
                assert box == demo[key]["expected_box"], \
                    f"demo {key} identity FAILED: {box} != {demo[key]['expected_box']}"
            demo_json[key] = {"x": tgt["x"], "y": tgt["y"], "w": tgt["w"],
                              "h": tgt["h"], "new": demo[key]["new"]}
    dna_reg_b64, dna_reg_name = _font_b64(dna_regular, LIB_SERIF_REG)
    dna_bold_b64, dna_bold_name = _font_b64(dna_bold, LIB_SERIF_BOLD)
    info["dna_fonts"] = {"regular": dna_reg_name, "bold": dna_bold_name}
    html = _template()
    # hardcoded 200-DPI background-size literals in the template's JS:
    html = html.replace("(1653 * S)", f"({W} * S)").replace("(2323 * S)", f"({H} * S)")
    assert "(1653 * S)" not in html and "(2323 * S)" not in html
    html = (html.replace("__W__", str(int(W * S))).replace("__H__", str(int(H * S)))
                .replace("__ORIG__", orig_b64).replace("__CLEAN__", clean_b64)
                .replace("__CLEAN_MANUAL__", manual_b64)
                .replace("__WORDS__", json.dumps(words))
                .replace("__DEMO__", json.dumps(demo_json))
                .replace("__SHORTLIST__", json.dumps(shortlist or []))
                .replace("__DNAFONT_REG__", dna_reg_b64)
                .replace("__DNAFONT_BOLD__", dna_bold_b64)
                .replace("__NWORDS__", str(len(words)))
                .replace("__PAGE_META__", json.dumps(page_meta))
                .replace("__S__", str(S)))
    assert "__PAGE_META__" not in html, "PAGE_META placeholder leaked into the built page"
    with open(out_path, "w") as f:
        f.write(html)
    return out_path, words, info
