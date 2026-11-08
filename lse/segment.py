"""Live-Scan word segmentation WITHOUT recognition (v5-300).

Ported from the GRAVORA prototype (scan-paper/segment.py, Round 6 Track B):
connected components -> lines -> words. No ML, no OCR, no character
reading. Output: word boxes + estimated font size.

This package version wraps the proven script body in segment_array()
(the algorithm is unchanged); segment_file() keeps the old
``segment.py IMAGE OUT.json`` behaviour for scripts. See API.md.
"""
import json
import os

import cv2
import numpy as np

from .deskew import correct, estimate_angle


def segment_array(img, image_name="", deskew=True):
    """Segment one page image (BGR numpy array, native DPI).

    Returns the seg dict: {"image", "method", "median_char_h_px",
    "sig_y_detected", "rescued_blobs", "words": [{"box", "line",
    "font_px", "n_comp", "src"?}]}. The input image is never modified;
    deskew (if enabled) rotates only a copy in memory, and only when
    |angle| >= 0.5 deg. Original file bytes are never touched.
    """

    # --- Round 2 step 5a: DESKEW as the first pipeline step ---
    # Estimate the skew (projection-profile peak + Hough cross-check) and rotate
    # ONLY if |angle| >= 0.5 deg. Below that the drift across the page width
    # (1650 px * tan(angle)) stays inside the line-grouping tolerance
    # (0.6 * med_h ~= 11 px; drift exceeds it at ~0.38 deg), so rotating would
    # only cost resampling blur: measured on the real pages, correcting May's
    # tiny +0.11 deg REGRESSED the hand-counted sample 33/37 -> 31/37, while
    # Aug's +0.26 deg was harmless (293 words, 37/37). Crooked pages are
    # rescued: +3.0 deg skewed totals 375 -> 285 after correction (true 293).
    # The original scan file is never overwritten; the corrected image lives
    # only in memory for this run.
    _gray0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _angle, _curve, _hough, _s0, _sb = estimate_angle(_gray0)
    print(f"deskew: correction angle {_angle:+.2f} deg (Hough {_hough}; "
          f"score gain {(_sb - _s0) / _s0 * 100:+.1f}%)")
    if abs(_angle) >= 0.5:
        img = correct(img, _angle)
        print(f"deskew: rotated by {_angle:+.2f} deg (threshold 0.5 deg)")
    else:
        print("deskew: |angle| < 0.5 deg -> no rotation (straight page, no resampling)")

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Binarize: Otsu. Text/lines are dark -> foreground.
    otsu_val, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    print(f"otsu threshold: {otsu_val}")

    num, labels, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    print(f"components raw: {num}")

    # region never segmented: logo (top-left image). The signature row is detected per page (below).
    LOGO = (150, 120, 510, 450)  # x1.5 (200-DPI coords)

    def in_excluded(x, y, ww, hh):
        cx, cy = x + ww / 2, y + hh / 2
        return LOGO[0] <= cx <= LOGO[2] and LOGO[1] <= cy <= LOGO[3]

    comps = []
    for i in range(1, num):
        x, y, ww, hh, area = stats[i]
        if area < 14:           # specks / noise (6 x 2.25)
            continue
        if in_excluded(x, y, ww, hh):
            continue
        # table rules / outer border / underlines: very long in one dimension, thin in the other
        if (ww > 375 and hh <= 15) or (hh > 150 and ww <= 15):  # V4-1 merged (300 DPI: 250/10, 100/10 x1.5)
            continue
        if ww > 900 or hh > 180:  # huge blobs (x1.5)
            continue
        comps.append({"x": int(x), "y": int(y), "w": int(ww), "h": int(hh), "area": int(area),
                      "cx": float(cent[i][0]), "cy": float(cent[i][1]), "lab": i})
    print(f"components kept (letter-like, before signature filter): {len(comps)}")

    # median character height -> line grouping tolerance
    heights = sorted(c["h"] for c in comps)
    med_h = heights[len(heights) // 2]
    print(f"median component height: {med_h}px")

    # --- ROUND 6 TRACK B (promoted): cluster-anchor signature zone ---
    # v4-300 flaw (Raviraj p2): sig_y = top of the FIRST tall stroke. A small
    # red date-stamp ("DTD 08/08/26", [819,1829,90,60]) is tall, so sig_y=1829
    # excluded the whole bottom 26% (362 comps). Fix: CLUSTER the tall strokes
    # by y-top (chaining gap 4.5*med_h) and anchor on the LARGEST cluster
    # (most strokes; tie -> lowest top) — the signature/stamp zone. A lone
    # tall stamp above the real zone forms its own 1-stroke cluster and is
    # ignored. The >=6-comps-below gate applies to the anchor top, as before.
    # Exclusion stays a full-width cutoff below the anchor top: the x-zone
    # variant (V-B) was measured and REJECTED — it leaked signature strokes
    # on PG pages (+28 words, aug-p5 +9/+10) because a narrow anchor x-range
    # does not cover a second signature on the other side. On all 14 PG pages
    # there is exactly one tall-stroke cluster, so this change is PG-identical
    # by construction (verified: 0 word changes, same sig_y, 14/14 pages).
    tall = [c for c in comps
            if c["y"] > 0.7 * h and c["h"] > 2.2 * med_h and c["w"] < 300]  # x1.5
    tall.sort(key=lambda c: c["y"])
    _CLUSTER_GAP = 4.5 * med_h
    _clusters = []
    for _c in tall:
        if _clusters and _c["y"] - _clusters[-1][-1]["y"] <= _CLUSTER_GAP:
            _clusters[-1].append(_c)
        else:
            _clusters.append([_c])
    print(f"tall-stroke clusters (gap {_CLUSTER_GAP:.0f}px): "
          f"{[(len(cl), min(c['y'] for c in cl), max(c['y'] for c in cl)) for cl in _clusters]}")
    sig_y = h
    if _clusters:
        _anchor = max(_clusters, key=lambda cl: (len(cl), -min(c["y"] for c in cl)))
        _cand_y = min(c["y"] for c in _anchor)
        _below = sum(1 for c in comps if c["cy"] > _cand_y)
        if _below >= 6:
            sig_y = _cand_y
            _zone = (min(c["x"] for c in _anchor), max(c["x"] + c["w"] for c in _anchor))
            print(f"signature zone detected: sig_y={sig_y} "
                  f"(anchor cluster {len(_anchor)}/{len(tall)} tall strokes, "
                  f"x-range {_zone}, {_below} comps below)")
        else:
            sig_y = h
            print(f"signature zone NOT detected: anchor {len(_anchor)} stroke(s) "
                  f"but only {_below} comps below -> no exclusion")
    else:
        sig_y = h
        print("no signature row detected (0 tall strokes) -> no exclusion")
    # V4-1 (continued): hollow-border / closed-rectangle filter. A field border
    # is a big box with very little ink (fill = area/(w*h) ~0.12-0.16); real text
    # fills >= ~0.24. Threshold 0.20 sits between. Runs AFTER tall detection so
    # signature strokes (fill ~0.08) can still trigger sig-row. Scaled x1.5.
    # MERGE FIX: also require frame-like ink (edge fraction >= 0.40) so a
    # highlight-dither mesh (uniform ink, edge 0.044) is NOT dropped.
    def _edge_frac(c):
        """Fraction of the component's own pixels within 5px of its bbox edge.
        Band is DPI-scaled: 3px at 200 DPI x1.5 = 5px at 300 DPI (a 300-DPI
        frame line is ~5-6px thick; a 3px band only catches its outer half)."""
        m = (labels[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]] == c["lab"])
        tot = int(m.sum())
        if tot == 0:
            return 0.0
        edge = m.copy()
        edge[5:-5, 5:-5] = False
        return float(edge.sum()) / tot
    _before_fill = len(comps)
    comps = [c for c in comps
             if not (c["w"] >= 120 and c["h"] >= 23 and c["area"] / (c["w"] * c["h"]) <= 0.20
                     and _edge_frac(c) >= 0.40)]
    print(f"hollow-border filter dropped {_before_fill - len(comps)} components (fill<=0.20, w>=120, h>=23, edge>=0.40)")
    comps = [c for c in comps if c["cy"] < sig_y]
    print(f"components after signature filter: {len(comps)}")

    # --- BUG 1 FIX: split a merged bold blob (e.g. highlighted title) into words ---
    def _extract_subs(ink_mask):
        """Connected components of a dark-ink mask -> letter-height pieces.
        Merged V4-6 + F4: 4-connectivity (F4 breaks halftone dot-chains at 300 DPI);
        area floor 34 = 15 x 2.25 (300-DPI scaling)."""
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(
            ink_mask.astype(np.uint8), connectivity=4)
        subs = []
        for i in range(1, n2):
            x, y, ww, hh, area = (int(v) for v in st2[i])
            if area < 34:  # 15 x 2.25
                continue
            if hh < 0.4 * med_h or hh > 2.5 * med_h:
                continue  # drops underline remnants and non-letter chunks
            subs.append((x, y, ww, hh))
        subs.sort(key=lambda s: s[0])
        return subs


    def _group_subs(subs, mult=2.0):
        """V4-6 TOP-2 rule (merged): split only at the two largest gaps that reach
        max(5, mult*median gap). Two multipliers, both measured:
        - normal subs mult=2.0: 2.2x REGRESSED the Aug p7 title (the
          ANALYTICAL|TEST gap, 8px = 2.0x the 4px median, fell below the 8.8px
          threshold, "ANALYTICAL TEST" stayed merged); 1.5x OVER-SPLIT (May
          pages +17..+21 words — letter gaps in single-word blobs qualified).
          2.0x is the measured sweet spot for normal subs.
        - eroded subs mult=1.5: erosion inflates ALL gaps (May p4 title median
          6px vs 4px uneroded), so the same 2.0x misses the 11px word gap and
          merges "ANALYTICAL TEST" (measured: 2.0x -> 2 title boxes on May p4,
          1.5x -> 3). Track C's v4 used 1.5x for eroded subs.
        The >= comparison is inclusive, so an 8px gap meets an 8.0px threshold."""
        if not subs:
            return []
        gaps, rmax = [], subs[0][0] + subs[0][2]
        for c in subs[1:]:
            gaps.append(c[0] - rmax)
            rmax = max(rmax, c[0] + c[2])
        med_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0
        thr = max(5, mult * med_gap)
        qual = sorted([i for i, g in enumerate(gaps) if g >= thr],
                      key=lambda i: -gaps[i])[:2]
        cuts = set(qual)
        groups, cur = [], [subs[0]]
        for i, c in enumerate(subs[1:]):
            if i in cuts:
                groups.append(cur)
                cur = [c]
            else:
                cur.append(c)
        groups.append(cur)
        return groups
        # NOTE (Round 4 merge, measured): a "merge groups with <3 subs" rule was
        # tried here to fix the THICKNESS/GRAMMAGE over-splits (a 13px LETTER gap
        # beats the Aug p7 title's 8px WORD gap, so no gap threshold separates
        # them). It made things WORSE: -7 words/page (it merged real 1-2-sub
        # tokens — dashes, dots, short words — back into their neighbours).
        # Reverted. The 3 over-splits (Aug p8 THICKNESS, May p3 THICKNESS +
        # GRAMMAGE) stay as a known open item for Round 5: they need a better
        # discriminator than gap size (e.g. a width/lexicon check), not a
        # lower threshold. The words are still fully covered and editable,
        # just in two pieces.


    def split_blob_words(bbox):
        """bbox = (x0, y0, x1, y1) of one merged component. Returns word boxes or []."""
        x0, y0, x1, y1 = bbox
        # letters are near-black; the grey highlight dither is mid-grey (May title:
        # letters grey 0-63, dither 96-191, paper 224-255; page Otsu 127).
        dark = int(0.65 * otsu_val)
        if dark < 64:
            dark = 128  # 300-DPI FIX F1: pure 1-bit image (Otsu 0) -> midpoint, else no ink
        ink = gray[y0:y1, x0:x1] < dark
        # strip solid rule/underline rows (row ink > 90% of the blob width)
        row_ink = ink.sum(axis=1)
        ink = ink.copy()
        ink[row_ink > 0.90 * ink.shape[1], :] = False
        subs = _extract_subs(ink)
        if not subs:
            return [], 0
        # V4-6 erosion fallback: in B&W the halftone dither bridges bold letters
        # into one wide piece. A 3x3 erosion breaks 1px bridges; letters survive.
        # Trigger: any sub wider than 2.5*med_h, or any negative (overlapping) gap.
        # Use the eroded subs only if they are plausibly letters.
        _maxw = max((s[2] for s in subs), default=0)
        _gaps0 = []
        if subs:
            _rm = subs[0][0] + subs[0][2]
            for _c in subs[1:]:
                _gaps0.append(_c[0] - _rm)
                _rm = max(_rm, _c[0] + _c[2])
        _eroded = False
        if subs and (_maxw > 2.5 * med_h or (subs and min(_gaps0, default=0) < 0)):
            ero = cv2.erode(ink.astype(np.uint8), np.ones((3, 3), np.uint8))
            subs_e = _extract_subs(ero)
            _maxw_e = max((s[2] for s in subs_e), default=0)
            if len(subs_e) >= 2 and _maxw_e <= 2.5 * med_h:
                print(f"blob-split erosion fallback: {len(subs)} subs "
                      f"(max w {_maxw}) -> {len(subs_e)} subs (max w {_maxw_e})")
                subs = subs_e
                _eroded = True
        groups = _group_subs(subs, mult=1.5 if _eroded else 2.0)
        # 300-DPI FIX F5: merge a lone narrow piece (spaced letter) into its neighbour
        _mg = []
        for _g in groups:
            if len(_g) == 1 and _g[0][2] < 0.7 * med_h and _mg:
                _mg[-1].extend(_g)
            else:
                _mg.append(_g)
        if len(_mg) > 1 and len(_mg[0]) == 1 and _mg[0][0][2] < 0.7 * med_h:
            _mg[1] = _mg[0] + _mg[1]
            _mg = _mg[1:]
        groups = _mg
        words = []
        for g in groups:
            wx0 = x0 + min(s[0] for s in g)
            wy0 = y0 + min(s[1] for s in g)
            wx1 = x0 + max(s[0] + s[2] for s in g)
            wy1 = y0 + max(s[1] + s[3] for s in g)
            words.append({"box": [wx0, wy0, wx1, wy1], "n_comp": len(g), "src": "blob-split"})
        # validation: the split must cover most of the blob with sane word geometry,
        # otherwise the blob stays dropped (never guessed).
        tot_w = sum(wd["box"][2] - wd["box"][0] for wd in words)
        ok = (len(words) >= 1 and tot_w >= 0.5 * (x1 - x0)
              and all((wd["box"][2] - wd["box"][0]) >= 0.5 * med_h
                      and (wd["box"][3] - wd["box"][1]) <= 2.5 * med_h for wd in words))
        return (words if ok else []), len(subs)

    # group into lines: sort by cy; new line when cy jumps > 0.6 * med_h from line's mean cy
    comps.sort(key=lambda c: (c["cy"], c["cx"]))
    lines = []
    for c in comps:
        placed = False
        # V4-3: tiny comps (decimal points, commas: w,h <= 0.40*med_h) attach by
        # BASELINE first — their centre-y sits ~8-11px below the line mean (a dot
        # is only 4-5px tall at the baseline at 200 DPI), so the cy test strands
        # them as singleton lines and they get dropped, splitting "700.0" into
        # "700." + "0". Tolerances scaled x1.5 for 300 DPI.
        if c["w"] <= 0.40 * med_h and c["h"] <= 0.40 * med_h:
            _bot = c["y"] + c["h"]
            _best, _bd = None, 1e9
            for ln in lines:
                _items = ln["items"]
                # baseline from NEARBY items only (within 150px in x): the whole
                # line's median bottom is dragged up by small letters and misses
                # the dot; the neighbouring digits sit on the same baseline.
                _near = [i for i in _items
                         if abs((i["x"] + i["w"] / 2) - (c["x"] + c["w"] / 2)) <= 150]
                _pool = _near if _near else _items
                _base = sorted(i["y"] + i["h"] for i in _pool)[len(_pool) // 2]
                _x0 = min(i["x"] for i in _items)
                _x1 = max(i["x"] + i["w"] for i in _items)
                if abs(_bot - _base) <= 5 and _x0 - 23 <= c["x"] <= _x1 + 23:
                    if abs(_bot - _base) < _bd:
                        _best, _bd = ln, abs(_bot - _base)
            if _best is not None:
                _best["items"].append(c)
                _best["cy_mean"] = sum(i["cy"] for i in _best["items"]) / len(_best["items"])
                placed = True
        if not placed:
            for ln in lines:
                if abs(c["cy"] - ln["cy_mean"]) <= max(9, 0.6 * med_h):  # 6 x 1.5
                    ln["items"].append(c)
                    ln["cy_mean"] = sum(i["cy"] for i in ln["items"]) / len(ln["items"])
                    placed = True
                    break
        if not placed:
            lines.append({"cy_mean": c["cy"], "items": [c]})

    # singleton lines: try the blob rescue; anything unrescued is still dropped.
    rescued = []   # {"bbox": [...], "words": [...]}
    kept_lines = []
    for ln in lines:
        if len(ln["items"]) >= 2:
            kept_lines.append(ln)
            continue
        c = ln["items"][0]
        # merged-text-blob gate: wide, short, dense (a stamp is squarer, a rule thinner)
        if c["w"] >= 6 * med_h and c["h"] <= 3 * med_h and c["area"] >= 37.5 * med_h:  # area x2.25 vs med_h x1.5
            bbox = (c["x"], c["y"], c["x"] + c["w"], c["y"] + c["h"])
            words, n_sub = split_blob_words(bbox)
            if words:
                print(f"rescued merged blob {list(bbox)} -> {len(words)} words ({n_sub} pieces)")
                rescued.append({"bbox": list(bbox), "words": words})
                kept_lines.append({"cy_mean": c["cy"], "items": [c], "rescued_words": words})
            else:
                print(f"singleton blob {list(bbox)}: split failed -> dropped")
        # else: ordinary singleton (speck / lone mark) -> dropped as before
    kept_lines.sort(key=lambda ln: ln["cy_mean"])
    print(f"text lines: {len(kept_lines)} (rescued singletons: {len(rescued)})")

    # within a line: sort by x, group into words by horizontal gap
    words = []
    for li, ln in enumerate(kept_lines):
        if "rescued_words" in ln:
            for wd in ln["rescued_words"]:
                x0, y0, x1, y1 = wd["box"]
                words.append({"box": [x0, y0, x1, y1], "line": li,
                              "font_px": round(float(y1 - y0), 1),
                              "n_comp": wd["n_comp"], "src": "blob-split"})
            continue
        items = sorted(ln["items"], key=lambda c: c["x"])
        gap_thresh = max(8, 0.30 * med_h)  # V4-4: 0.35 -> 0.30 (300 DPI floor 8)
        cur = [items[0]]
        groups = []
        for prev, c in zip(items, items[1:]):
            gap = c["x"] - (prev["x"] + prev["w"])
            if gap > gap_thresh:
                groups.append(cur)
                cur = [c]
            else:
                cur.append(c)
        groups.append(cur)
        for grp in groups:
            x0 = min(c["x"] for c in grp); y0 = min(c["y"] for c in grp)
            x1 = max(c["x"] + c["w"] for c in grp); y1 = max(c["y"] + c["h"] for c in grp)
            words.append({"box": [x0, y0, x1, y1], "line": li,
                          "font_px": round(float(y1 - y0), 1),
                          "n_comp": len(grp), "_comps": grp})

    # suppress normal words that lie entirely inside a rescued blob: they are
    # fragments of the blob's highlight edge, not real words (May title had 3).
    if rescued:
        before = len(words)
        blobs = [r["bbox"] for r in rescued]
        words = [wd for wd in words
                 if wd.get("src") == "blob-split" or not any(
                     wd["box"][0] >= b[0] and wd["box"][1] >= b[1]
                     and wd["box"][2] <= b[2] and wd["box"][3] <= b[3] for b in blobs)]
        print(f"suppressed {before - len(words)} fragment words inside rescued blobs")

    # --- v3: split merged wide word boxes (e.g. August title) ---
    # A merged bold blob can ALSO survive as a normal word box when its line has
    # >= 2 items (the singleton rescue above never runs): the whole title becomes
    # ONE word box, overlapping the fragment words inside it. Gate: very wide for
    # its component count (letters merged into few components) + short.
    # split_blob_words validates the split itself; a failed split keeps the word.
    def _inside(a, b):
        return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]

    split_boxes, out, split_done = [], [], 0
    for wd in words:
        if wd.get("src") == "blob-split":
            out.append(wd)
            continue
        x0, y0, x1, y1 = wd["box"]
        wpx, hpx = x1 - x0, y1 - y0
        ncomp = max(1, wd.get("n_comp", 1))
        if (wpx >= 6 * med_h and hpx <= 3 * med_h):  # 300-DPI FIX F2: no ncomp gate; split_blob_words validates
            parts, n_sub = split_blob_words((x0, y0, x1, y1))
            if len(parts) >= 2:
                print(f"split merged word box {wd['box']} -> {len(parts)} words ({n_sub} pieces)")
                for p in parts:
                    out.append({"box": p["box"], "line": wd["line"],
                                "font_px": round(float(p["box"][3] - p["box"][1]), 1),
                                "n_comp": p["n_comp"], "src": "blob-split"})
                split_boxes.append(wd["box"])
                split_done += 1
                continue
        out.append(wd)
    words = [wd for wd in out if wd.get("src") == "blob-split"
             or not any(_inside(wd["box"], b) for b in split_boxes)]
    print(f"merged word boxes split: {split_done}")

    # --- 300-DPI FIX F3: drop words overlapping a larger kept word by >50% ---
    # (highlight-edge / underline fragments overlapping rescued or split title words)
    def _overlap_area(a, b):
        _x0, _y0 = max(a[0], b[0]), max(a[1], b[1])
        _x1, _y1 = min(a[2], b[2]), min(a[3], b[3])
        return max(0, _x1 - _x0) * max(0, _y1 - _y0) if _x1 > _x0 and _y1 > _y0 else 0
    _by_area = sorted(words, key=lambda wd: (wd["box"][2] - wd["box"][0]) * (wd["box"][3] - wd["box"][1]), reverse=True)
    _kept, _dropped_overlap = [], 0
    for _wd in _by_area:
        _area = (_wd["box"][2] - _wd["box"][0]) * (_wd["box"][3] - _wd["box"][1])
        if any(_overlap_area(_wd["box"], _k["box"]) > 0.5 * _area for _k in _kept):
            print(f"dropped overlapping fragment {_wd['box']}")
            _dropped_overlap += 1
            continue
        _kept.append(_wd)
    words = sorted(_kept, key=lambda wd: (wd.get("line", 0), wd["box"][0]))
    print(f"overlapping fragments dropped: {_dropped_overlap}")

    # V4-5 dash split: a dash-like component (flat and wide: h <= 0.30*med_h,
    # w >= 0.5*med_h) flanked by >=5px gaps on both sides is its own token
    # ("6.0 - 8.0" -> "6.0" | "-" | "8.0"). A hyphen joining a word
    # ("Heat-Seal", gaps ~0px) is untouched; a leading minus ("- 58.54")
    # splits off the same way. Only runs on normal grouped words.
    def _dash_split(wd):
        grp = wd.get("_comps")
        if not grp or len(grp) < 3:
            return [wd]
        items = sorted(grp, key=lambda c: c["x"])
        cuts = []
        for i, c in enumerate(items):
            if c["h"] <= 0.30 * med_h and c["w"] >= 0.5 * med_h:
                # neighbours must be real characters (h >= 0.5*med_h): without
                # this, flat RULE FRAGMENTS split each other.
                gl = c["x"] - (items[i - 1]["x"] + items[i - 1]["w"]) if i > 0 else 99
                gr = items[i + 1]["x"] - (c["x"] + c["w"]) if i < len(items) - 1 else 99
                left_ok = (i == 0) or (items[i - 1]["h"] >= 0.5 * med_h and gl >= 5)
                right_ok = (i == len(items) - 1) or (items[i + 1]["h"] >= 0.5 * med_h and gr >= 5)
                if left_ok and right_ok:
                    cuts.append(i)
        if not cuts:
            return [wd]
        parts, cur = [], []
        for i, c in enumerate(items):
            if i in cuts:
                if cur:
                    parts.append(cur)
                parts.append([c])
                cur = []
            else:
                cur.append(c)
        if cur:
            parts.append(cur)
        out = []
        for grp2 in parts:
            x0 = min(c["x"] for c in grp2); y0 = min(c["y"] for c in grp2)
            x1 = max(c["x"] + c["w"] for c in grp2); y1 = max(c["y"] + c["h"] for c in grp2)
            out.append({"box": [x0, y0, x1, y1], "line": wd["line"],
                        "font_px": round(float(y1 - y0), 1),
                        "n_comp": len(grp2), "_comps": grp2})
        return out

    _dashed, _ndash = [], 0
    for wd in words:
        if wd.get("src") == "blob-split":
            _dashed.append(wd)
            continue
        _parts = _dash_split(wd)
        if len(_parts) > 1:
            _ndash += 1
        _dashed.extend(_parts)
    words = _dashed
    print(f"dash splits: {_ndash}")

    # strip internal component lists (output format identical to v3)
    for _wd in words:
        _wd.pop("_comps", None)
    print(f"words segmented: {len(words)}")
    return {"image": image_name, "method": "connected-components, no recognition "
            "(v5-300: v4-300 + R6 cluster-anchor signature zone)",
            "median_char_h_px": med_h, "sig_y_detected": sig_y,
            "rescued_blobs": rescued, "words": words}

def segment_file(img_path, out_path=None, deskew=True):
    """Read an image file, segment it, optionally write the seg JSON."""
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(img_path)
    seg = segment_array(img, image_name=img_path, deskew=deskew)
    if out_path:
        with open(out_path, "w") as f:
            json.dump(seg, f, indent=1)
        print(f"saved: {out_path}")
    return seg


if __name__ == "__main__":
    import sys
    _seg = segment_file(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"words segmented: {len(_seg['words'])}")
