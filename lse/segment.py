"""Live-Scan word segmentation WITHOUT recognition (v5-300).

Round 20 merged baseline (promoted 2026-11-08): Round 4 Track A
native-300-DPI scaling + fixes F1-F6, Round 4 Track C v4 rules
(V4-1..V4-6), Round 6 Track B cluster-anchor signature zone, plus
Round 19: per-page logo exclusion rect (logo_detect), sig_y anchor
check (sign-off-zone validation), top2a all-cuts/subcov/row-split
blob splitter, top2b rhythm-DP fallback; plus Round 20: p21
dark-core reclaim (reclaim2c, after validation only) and the G2
gateside rule (in gate.py). See improve/ROUND20-REPORT.md for
measurements (Raviraj gate 17/8 -> 23/2).

Connected components -> lines -> words. No ML, no OCR, no character
reading. Output: word boxes + estimated font size. The input image is
never modified; deskew (if enabled) rotates only a copy in memory,
and only when |angle| >= 0.5 deg. Original file bytes are never touched.
"""
import json

import cv2
import numpy as np

from .deskew import correct, estimate_angle
from .logo_detect import detect_logo_rect

# Track 2b (Round 19): Rhythm-DP blob splitter lives next to this file.
try:
    from .rhythm_dp import rhythm_dp_words as _rhythm_dp_words
except Exception:
    _rhythm_dp_words = None


def segment_array(img, image_name="", deskew=True):
    """Segment one page image (BGR numpy array, native DPI).

    Returns the seg dict: {"image", "method", "median_char_h_px",
    "sig_y_detected", "logo_rect_detected", "rescued_blobs", "words":
    [{"box", "line", "font_px", "n_comp", "src"?}]}. The input image is
    never modified; deskew (if enabled) rotates only a copy in memory,
    and only when |angle| >= 0.5 deg. Original file bytes are never
    touched.
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
    if deskew:
        _gray0 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _angle, _curve, _hough, _s0, _sb = estimate_angle(_gray0)
        print(f"deskew: correction angle {_angle:+.2f} deg (Hough {_hough}; "
              f"score gain {(_sb - _s0) / _s0 * 100:+.1f}%)")
    else:
        _angle = 0.0
        print("deskew: disabled (deskew=False) -> no rotation")
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

    # --- ROUND 19 TRACK-LOGO: detect the page's own logo exclusion rect ---
    # (replaces the fixed LOGO rect; runs on the same deskewed gray image and
    # the same Otsu/CCs the pipeline below uses, so the decision is per page
    # and reproducible from the seg log alone).
    LOGO, _logo_info = detect_logo_rect(gray)
    print(f"logo exclusion: detected rect {LOGO} (fixed (150,120,510,450) removed;"
          f" None = no logo graphic in the letterhead zone -> no exclusion)"
          f" info={_logo_info}")

    # region never segmented: logo (top-left image). The signature row is detected per page (below).
    # ROUND 19 TRACK-LOGO: the fixed rect (150,120,510,450) is GONE. It ate real
    # Raviraj letterhead text (CITY, Corporate, consign, IN, GO, ORIGINAL...;
    # DIAGNOSIS.md §6.1). The exclusion rect is now detected per page by
    # logo_detect.detect_logo_rect() (called just above, on the same deskewed
    # gray image): the real logo graphic's bbox + frame + caption, or None when
    # the page has no logo graphic in the letterhead zone. LOGO is set by that
    # call (not re-initialised here — the detection result must survive).
    # The original segment.py is untouched; this file is the track-local copy.


    def in_excluded(x, y, ww, hh):
        if LOGO is None:
            return False
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

    # --- Track 2b (Round 19): page-learned letter pitch for the Rhythm DP ---
    # Median width of page-wide dark-ink letter pieces / 0.8 (letters fill
    # ~80% of their advance on average). Measured stable: p21 15.0 (true ~16),
    # aug-p1 20.0, may-p1 22.5, rav-p2 16.2. The DP is insensitive to +-20%
    # pitch error (probe: 42/42 certain boundaries at pitch 13/16/19), so
    # this estimate only feeds the rhythm tiebreak, never a threshold.
    PITCH = 0.57 * med_h
    try:
        _dark_thr = int(0.65 * otsu_val)
        if _dark_thr < 64:
            _dark_thr = 128
        _n2, _l2, _st2, _ = cv2.connectedComponentsWithStats(
            (gray < _dark_thr).astype(np.uint8), connectivity=4)
        _dw = [int(s[2]) for s in _st2[1:]
               if int(s[4]) >= 34 and 0.4 * med_h <= int(s[3]) <= 2.5 * med_h
               and int(s[2]) <= 2.5 * med_h]
        if _dw:
            PITCH = float(np.median(_dw)) / 0.8
    except Exception as _e:
        print(f"pitch estimation failed ({_e}) -> fallback 0.57*med_h")
    print(f"track-2b letter pitch: {PITCH:.1f}px (dark pieces n={len(_dw) if '_dw' in dir() else 0})")

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
    # --- ROUND 19 TRACK-SIGY (anchor validation; sign-off-zone heuristic, S30) ---
    # A genuine signature zone has handwriting/stamps below the anchor, NOT
    # regular printed text lines. If the region below the anchor contains
    # >=3 regular print lines AND >=100 print-like components, the anchor is
    # NOT a signature zone — it is a stamp graphic ("?" outline, seal arc)
    # or a table-rule fragment sitting above ordinary printed content, and
    # the exclusion must NOT fire (else a whole printed block is dropped
    # from the seg, hidden from the gate too).
    # Print line = cy-band (tol 0.5*med_h) with n>=8, x-span>=400px and
    # >=70% of comps with h in [0.6,1.4]*med_h. Measured on 32 pages
    # (25 Raviraj + 5 PG + 2 canonical): genuine anchors max 1 line / 70
    # print-like; bogus anchors min 3 lines / 127 print-like; the rule is
    # stable under parameter perturbation (n 6-8, span 300-400, reg 0.6-0.7,
    # print-like 80-100 all give the same classification — see
    # printline_probe.json). No OCR, no model, rule-only.
    def _print_lines_below(comps_below, med_h):
        if not comps_below:
            return 0, 0
        n_pl = sum(1 for c in comps_below if 0.6 * med_h <= c["h"] <= 1.4 * med_h)
        srt = sorted(comps_below, key=lambda c: c["cy"])
        bands = []
        for c in srt:
            if bands and c["cy"] - bands[-1][-1]["cy"] <= 0.5 * med_h:
                bands[-1].append(c)
            else:
                bands.append([c])
        n_lines = 0
        for b in bands:
            n = len(b)
            if n < 8:
                continue
            x0 = min(c["x"] for c in b)
            x1 = max(c["x"] + c["w"] for c in b)
            if x1 - x0 < 400:
                continue
            reg = sum(1 for c in b if 0.6 * med_h <= c["h"] <= 1.4 * med_h) / n
            if reg >= 0.7:
                n_lines += 1
        return n_lines, n_pl

    sig_y = h
    if _clusters:
        _anchor = max(_clusters, key=lambda cl: (len(cl), -min(c["y"] for c in cl)))
        _cand_y = min(c["y"] for c in _anchor)
        _below = sum(1 for c in comps if c["cy"] > _cand_y)
        if _below >= 6:
            _below_comps = [c for c in comps if c["cy"] > _cand_y]
            _n_pl_lines, _n_pl = _print_lines_below(_below_comps, med_h)
            if _n_pl_lines >= 3 and _n_pl >= 100:
                sig_y = h
                print(f"signature zone REJECTED: anchor {len(_anchor)} stroke(s) "
                      f"at y={_cand_y} but {_n_pl_lines} print lines / {_n_pl} "
                      f"print-like comps below -> stamp/table graphic, not a "
                      f"signature zone; no exclusion (sig_y=h)")
            else:
                sig_y = _cand_y
                _zone = (min(c["x"] for c in _anchor), max(c["x"] + c["w"] for c in _anchor))
                print(f"signature zone detected: sig_y={sig_y} "
                      f"(anchor cluster {len(_anchor)}/{len(tall)} tall strokes, "
                      f"x-range {_zone}, {_below} comps below; "
                      f"print-lines-below={_n_pl_lines}, print-like={_n_pl})")
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
    _comps_pre_sig = list(comps)
    comps = [c for c in comps if c["cy"] < sig_y]
    print(f"components after signature filter: {len(comps)}")

    # --- ROUND 21 FIX B (track-misses): 2D footer pass ---
    # The 1D sig_y cutoff structurally drops printed footer lines that share
    # the page bottom with the signature zone (DIAGNOSIS20: 53 words — p01 13
    # + p21 32 clean print, plus p01's 8 stamp-fused CARRIER NAME words which
    # stay out). Threshold-tuning cannot fix a 1D/2D mismatch, so the rescue is
    # 2D: group the below-sig_y comps with the pipeline's own mean line rule,
    # and keep a line's PRINT-LIKE comps (h in [0.6,1.4]*line_med_h, the line's
    # own median — rev.1) when they form a real print line: n_pl >= 6,
    # x-span >= 200px, median print-like height in [0.7,1.4]*med_h (page).
    # Guard margins are measured, not guessed: p01 footer median 27 vs cap 28
    # (1.4*20); p2 line-2 median 28 vs cap 28 (boundary); aug-p1 signature
    # line median ~41 vs cap 36.4 (rejected); p20 lines median 20 vs cap 19.6
    # (rejected); p21 show-through median 9 vs floor 19.6 (rejected); p21
    # "Yours faithfully," span 207 vs floor 200. Tall signature strokes
    # (h > 2.2*med_h), the p01
    # stamp-fused CARRIER NAME CCs (h 57-71), and p21's show-through line
    # (h 5-15, reg 0.00) all fail the test. Kept comps re-enter the normal
    # line/word grouping below, so footer words are ordinary words (no new
    # machinery, no new src). Measured bands (footer_lines.py): p01 lines 1+3
    # pass (Vehicle line + Value/Operator line = 13 words); p21 lines 1, 5, 6,
    # 10 pass (Yours faithfully, + Vice/SP zone + address = 32 words);
    # p2 lines 0+2 pass (2 real print lines below its sig_y — verified by eye,
    # canonical-checked); aug/may/p20 pass nothing (max n_pl 4 among non-print
    # lines). No OCR anywhere.
    _footer_kept = []
    _below = [c for c in _comps_pre_sig if c["cy"] >= sig_y]
    if _below and sig_y < h:
        _below.sort(key=lambda c: (c["cy"], c["cx"]))
        _flines = []
        for _c in _below:
            _placed = False
            for _ln in _flines:
                if abs(_c["cy"] - _ln["cy_mean"]) <= max(9, 0.6 * med_h):
                    _ln["items"].append(_c)
                    _ln["cy_mean"] = sum(i["cy"] for i in _ln["items"]) / len(_ln["items"])
                    _placed = True
                    break
            if not _placed:
                _flines.append({"cy_mean": _c["cy"], "items": [_c]})
        _hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        for _ln in _flines:
            # ROUND 21 FIX B rev.1: the print-like window is relative to the
            # LINE's own median height, not the page med_h — p01's footer font
            # is bigger than its body (caps h 29-30 vs med_h 20); the page
            # window [0.6,1.4]*20=[12,28] dropped every cap letter ("V" of
            # Vehicle, "D" of Dimension, "S" of Signature...). The page-median
            # guard below still rejects signature/show-through lines.
            _lhs = sorted(c["h"] for c in _ln["items"])
            _line_med = _lhs[len(_lhs) // 2]
            _pl = [c for c in _ln["items"] if 0.6 * _line_med <= c["h"] <= 1.4 * _line_med]
            if len(_pl) < 6:
                continue
            _span = max(c["x"] + c["w"] for c in _pl) - min(c["x"] for c in _pl)
            if _span < 300:
                continue
            _hs = sorted(c["h"] for c in _pl)
            _med_pl = _hs[len(_hs) // 2]
            if not (0.7 * med_h <= _med_pl <= 1.4 * med_h):
                continue
            # Saturation filter: black print ink has median saturation 0-15;
            # purple/blue stamp ink ~85 (measured: p21 round-seal letters 87
            # vs all footer print <= 15). A seal letter passes the geometry
            # test (it IS letter-shaped) but its ink is coloured; excluding it
            # keeps the footer pass from turning seal lettering into words
            # (p21's false-add [1904,2702,1972,2763] "OR AG" of the round seal
            # in variant AB). Conservative: only excludes, never adds.
            _pl2 = []
            for _c in _pl:
                _m = (labels[_c["y"]:_c["y"] + _c["h"], _c["x"]:_c["x"] + _c["w"]] == _c["lab"])
                if int(_m.sum()) == 0:
                    continue
                _sat = _hsv[_c["y"]:_c["y"] + _c["h"], _c["x"]:_c["x"] + _c["w"], 1][_m]
                if float(np.median(_sat)) > 40:
                    continue
                _pl2.append(_c)
            if len(_pl2) < 6:
                continue
            _span2 = max(c["x"] + c["w"] for c in _pl2) - min(c["x"] for c in _pl2)
            if _span2 < 200:
                continue
            _footer_kept.extend(_pl2)
            print(f"footer pass: kept line cy={_ln['cy_mean']:.0f} "
                  f"({len(_pl2)}/{len(_ln['items'])} print-like, span {_span2})")
        if _footer_kept:
            comps.extend(_footer_kept)
            print(f"footer pass: kept {len(_footer_kept)} comps below sig_y "
                  f"(of {len(_below)}); total comps now {len(comps)}")


    # --- BUG 1 FIX: split a merged bold blob (e.g. highlighted title) into words ---
    def _extract_subs(ink_mask, area_floor=34, h_floor=0.4):
        """Connected components of a dark-ink mask -> letter-height pieces.
        Merged V4-6 + F4: 4-connectivity (F4 breaks halftone dot-chains at 300 DPI);
        area floor 34 = 15 x 2.25 (300-DPI scaling).
        Round 20 track-p21 v2: core subs (grey<140) use area_floor=20 — a light
        "g" fragments vertically at 140 (bowl 51 / mid 31 / bottom 26 px on p13);
        the 34 floor dropped the descender pieces, so the orphan box covered
        only the bowl and the gate core stuck out below (new T1 0.505). Dark
        subs keep 34 (unchanged behaviour for grouping).
        v2b: the binding constraint was actually the HEIGHT floor (0.4*med_h):
        the "g" descender fragments are 6-7px tall < 0.4*21=8.4, so they never
        became core subs at all. Core subs use h_floor=0.25 (5.25px at med_h 21)
        — the orphan width/height/overlap guards still filter junk; a lone
        6px fragment is too narrow to be an orphan on its own, it only joins
        its own letter via the 2D clustering."""
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(
            ink_mask.astype(np.uint8), connectivity=4)
        subs = []
        for i in range(1, n2):
            x, y, ww, hh, area = (int(v) for v in st2[i])
            if area < area_floor:
                continue
            if hh < h_floor * med_h or hh > 2.5 * med_h:
                continue  # drops underline remnants and non-letter chunks
            subs.append((x, y, ww, hh))
        subs.sort(key=lambda s: s[0])
        return subs


    def _group_subs(subs, mult=2.0):
        """Round 19 Track 2a: split at ALL gaps that reach max(5, mult*median gap)
        — Round 20 track-p21: the floor is now max(8, 0.30*med_h, mult*med_gap),
        the main pipeline's own word-gap floor (V4-4). A blob-splitter cutting at
        6px contradicts the pipeline's word definition (gaps <= that are letter
        gaps): p21 "allotted" was cut at a 6px letter gap (med_gap 3, thr 6).
        The Aug/May title word gap is 8px at med_h 26 (floor 8.0, >= inclusive)
        so the measured title behaviour is preserved — verified by the 25+6 run.
        (TOP-2 cap removed — the old rule kept only the two largest gaps, silently
        dropping middle pieces; measured cause of 58/73 R19 flags, e.g. Ambawadi
        "wa"+"a" lost while tot_w 61.7% still passed). Principle: XY-cut/RLSA —
        cut at every significant valley (S15, track-online RESEARCH.md §2.4).
        Two multipliers, both measured (unchanged):
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
        # R19-fix (Aug p1 email "pgfoils@pgfoils.in", 2026-11-08) — RESTORED by the
        # Round 20 merge: the R20 tracks were built from a pre-fix copy of the R19
        # segmenter, so this was missing from reclaim2c. For ERODED subs (mult 1.5)
        # the median gap is taken over STRICTLY POSITIVE gaps only. Erosion inflates
        # gaps and leaves zero/negative gaps from subs that touch or overlap (a big
        # merged sub overlapping smaller subs); those are not gaps at all, and
        # including them drags the median down so the threshold cuts inside words.
        # Measured on the Aug p1 email blob (eroded): all-gap median 8 -> thr 12
        # (over-splits "pgfoils.in" into 3 fragments); positive-gap median 26 ->
        # thr 39 (exactly the 2 correct words). Uneroded subs (mult 2.0) keep the
        # all-gap median — changing it there REGRESSED a real split (Aug p1 y~2457:
        # an 11px word gap fell below a threshold raised 10 -> 12, merging two
        # words). So this applies to eroded subs only.
        if mult < 2.0:
            _pos = [g for g in gaps if g > 0]
            med_gap = sorted(_pos)[len(_pos) // 2] if _pos else 0
        else:
            med_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0
        thr = max(5, mult * med_gap)  # R20-p21 ablation v2b: floor OFF, reclaim v2b only
        cuts = set(i for i, g in enumerate(gaps) if g >= thr)  # R19-2a: ALL qualifying gaps
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


    def _subcov_c(subs_u, words, x0, y0):
        """Round 19 Track 2a — ink reconciliation (D8 scaledp principle:
        "the ink decides how many boxes exist"). Fraction of UNERODED subs whose
        centre (+-2px) lies inside some word box. Measured separation on 41 pages
        (2280 split calls, TOP-2 splits): canonical p2/p3 splits all 1.0; PG all
        1.0 except 8 title/email splits (0.75-0.923); all diagnosed bad Raviraj
        splits <1.0 (Ambawadi 0.800, Ahmedabad 0.636, p21 line blob 0.639).
        The naive tot_w/blob-width >=0.90 check was MEASURED WRONG (good Aug
        title splits score 0.63-0.78) and is NOT used here."""
        if not subs_u or not words:
            return 0.0 if subs_u else 1.0
        cov = 0
        for _s4 in subs_u:
            sx, sy, sw, sh = _s4[:4]  # subs may carry a 5th element (holes)
            cx, cy = x0 + sx + sw / 2, y0 + sy + sh / 2
            if any(wd["box"][0] - 2 <= cx <= wd["box"][2] + 2
                   and wd["box"][1] - 2 <= cy <= wd["box"][3] + 2 for wd in words):
                cov += 1
        return cov / len(subs_u)


    def _gap_mark(sub, words, x0, y0):
        """Round 21 Track D — is this uneroded sub a GAP MARK rather than a
        dropped letter-piece? A gap mark (a) lies strictly between two word
        boxes (a word box ends to its left and another starts to its right),
        (b) overlaps NO word box in x, (c) overlaps some word box in y (it sits
        on the same text line), and (d) is narrower than the pipeline's own
        minimum word width (0.5*med_h — the same constant the geometry check
        uses: a word box must be >= 0.5*med_h wide). A component narrower than
        any word can be, sitting wholly in a word gap and touching no word,
        cannot be a word — it is a free-standing mark ("@", ".", ",") that
        belongs to no word. No NEW constant is introduced: 0.5*med_h is the
        existing minimum-word-width. (The "@" inner ring: 13px = 0.50*med_h at
        med_h 26, gap-confined, x-overlap 0.)"""
        (sx, sy, sw, sh) = sub
        if sw > 0.5 * med_h:
            return False
        ax0, ay0, ax1, ay1 = x0 + sx, y0 + sy, x0 + sx + sw, y0 + sy + sh
        left = right = False
        for wd in words:
            bx0, by0, bx1, by1 = wd["box"]
            if min(ax1, bx1) - max(ax0, bx0) > 0:
                return False
            if bx1 <= ax0:
                left = True
            if bx0 >= ax1:
                right = True
        if not (left and right):
            return False
        # (c) sits on the same text line: y-overlap with some word box.
        return any(max(0, min(ay1, wd["box"][3]) - max(ay0, wd["box"][1])) > 0
                   for wd in words)


    def _all_subs_accounted(subs_u, words, x0, y0):
        """Round 21 Track D — complete ink reconciliation WITHOUT a tuned
        fraction: every uneroded sub is either COVERED (its centre, +-2px, lies
        inside some word box — the _subcov_c test) or a GAP MARK (_gap_mark).
        A split that leaves a real letter-piece unaccounted for is invalid.
        Returns True iff no sub is left unaccounted."""
        if not subs_u:
            return True
        if not words:
            return False
        for _s4 in subs_u:
            sx, sy, sw, sh = _s4[:4]  # subs may carry a 5th element (holes)
            cx, cy = x0 + sx + sw / 2, y0 + sy + sh / 2
            if any(wd["box"][0] - 2 <= cx <= wd["box"][2] + 2
                   and wd["box"][1] - 2 <= cy <= wd["box"][3] + 2 for wd in words):
                continue
            if _gap_mark((sx, sy, sw, sh), words, x0, y0):
                continue
            return False
        return True


    def _reclaim_core(words, core_subs, x0, y0, core_subs_ext=None):
        """Round 20 track-p21 (b) — dark-core reclaim.

        Root cause (measured on p21, otsu=184 -> dark=0.65*otsu=119 < CORE_THR=140):
        letters grey 120-140 have a gate dark core (grey<140) but NO dark sub at
        119, so the split either clips them (word box ends mid-letter -> T1 core
        sticks out: p21 0.598/0.539/0.525) or drops them entirely (subcov cannot
        see a sub that does not exist -> T2: "a" of allotted, "ng" of their,
        whole word "of"). Raising dark to 140 was MEASURED WRONG as a grouping
        threshold (blob [1693,1569,2028,1600]: 4 groups -> 1 bridged group;
        blob [555,1684,2028,1724]: "from"+"any" bridged into one group) — so
        dark stays 119 for GROUPING and the 140-subs are used ONLY here, as a
        post-grouping coverage check:
          (1) a 140-sub overlapping exactly ONE word box extends that box to
              cover the sub (the clipped letter is reclaimed; T1 fixed);
          (2) a 140-sub overlapping TWO OR MORE boxes is skipped — it bridges
              a cut, and guessing its side would steal a neighbour's letter;
          (3) a 140-sub overlapping NO box becomes its own word box
              ("core-reclaim") if it is word-like (width in [0.5, 3.0]*med_h;
              height already capped by _extract_subs) and does not overlap an
              existing box by >50% of its own area.
        No OCR, no model: the check uses only the page's own darker ink.
        Returns (words, n_extended, n_orphan_boxes)."""
        if not core_subs and not core_subs_ext:
            return words, 0, 0
        if core_subs_ext is None:
            core_subs_ext = core_subs
        if not core_subs:
            core_subs = core_subs_ext
        boxes = [list(w["box"]) for w in words]
        srcs = [w.get("src", "blob-split") for w in words]

        def _xov(a0, a1, b0, b1):
            return max(0, min(a1, b1) - max(a0, b0))
        n_ext = 0
        # Round 20 IoU fix (2026-11-08): the extension uses the ERODED subs
        # (core_subs_ext), tight to the letter core. The raw 140-subs are puffy
        # (grey fringe + merged underline/halftone/neighbours) and extending a
        # box to their full bbox over-extends it by 1-3px, dropping IoU below
        # 0.9 on May p1 / Aug p8 (the R10m reference hugs the glyph). Eroding
        # the 140-mask by 1px (3x3) breaks the thin bridges and removes the
        # fringe, so the extension hugs the glyph. The ORPHANS still use the
        # ORIGINAL subs (collected below) — eroding would shrink the p21
        # dropped letters and break the "@" gap-position rule, which both need
        # the un-eroded subs.
        # FALLBACK (p21): erosion can DESTROY a fragile light-letter fragment
        # (a 3px stem erodes to nothing), leaving no eroded sub to extend the
        # box — the clipped letter's core then sticks out again (T1 returns,
        # p21 ALLOW->REFUSE). So for each ORIGINAL sub, use the UNION of the
        # eroded pieces overlapping it; if no eroded piece overlaps it
        # significantly (>= 50% of the original's area), fall back to the
        # ORIGINAL sub's bbox so the extension still happens.
        def _ov_area(a, b):
            _ox = max(0, min(a[2], b[2]) - max(a[0], b[0]))
            _oy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
            return _ox * _oy
        _ext_subs = []
        for (sx, sy, sw, sh) in core_subs:
            _ax0, _ay0, _ax1, _ay1 = x0 + sx, y0 + sy, x0 + sx + sw, y0 + sy + sh
            _parts = []
            for (ex, ey, ew, eh) in core_subs_ext:
                _bx0, _by0, _bx1, _by1 = x0 + ex, y0 + ey, x0 + ex + ew, y0 + ey + eh
                if _ov_area((_ax0, _ay0, _ax1, _ay1), (_bx0, _by0, _bx1, _by1)) > 0:
                    _parts.append((_bx0, _by0, _bx1, _by1))
            if _parts:
                _ux0 = min(p[0] for p in _parts); _uy0 = min(p[1] for p in _parts)
                _ux1 = max(p[2] for p in _parts); _uy1 = max(p[3] for p in _parts)
                _ov = _ov_area((_ax0, _ay0, _ax1, _ay1), (_ux0, _uy0, _ux1, _uy1))
                _orig_area = (_ax1 - _ax0) * (_ay1 - _ay0)
                if _ov >= 0.5 * _orig_area:
                    _ext_subs.append((_ux0 - x0, _uy0 - y0, _ux1 - _ux0, _uy1 - _uy0))
                else:
                    _ext_subs.append((sx, sy, sw, sh))
            else:
                _ext_subs.append((sx, sy, sw, sh))
        for (sx, sy, sw, sh) in _ext_subs:
            ax0, ay0, ax1, ay1 = x0 + sx, y0 + sy, x0 + sx + sw, y0 + sy + sh
            ov = [i for i, b in enumerate(boxes)
                  if _xov(ax0, ax1, b[0], b[2]) > 0 and _xov(ay0, ay1, b[1], b[3]) > 0]
            if len(ov) == 1:
                i = ov[0]
                nb = [min(boxes[i][0], ax0), min(boxes[i][1], ay0),
                      max(boxes[i][2], ax1), max(boxes[i][3], ay1)]
                if nb[3] - nb[1] <= 2.5 * med_h:  # never let reclaim make a tall box
                    if nb != boxes[i]:
                        n_ext += 1
                    boxes[i] = nb
            # len(ov) >= 2: bridged across a cut, do not guess a side.
            # len(ov) == 0: not an extension candidate; orphans are collected
            # from the ORIGINAL subs below, not here.
        out = []
        for w, b in zip(words, boxes):
            nw = dict(w)
            nw["box"] = b
            out.append(nw)
        # Orphan collection from the ORIGINAL (uneroded) subs: a sub overlapping
        # no (extended) box is an orphan candidate. Using the original subs here
        # keeps the p21 dropped-letter detection and the "@" gap-position rule
        # exactly as before.
        orphans = []
        for (sx, sy, sw, sh) in core_subs:
            ax0, ay0, ax1, ay1 = x0 + sx, y0 + sy, x0 + sx + sw, y0 + sy + sh
            ov = [i for i, b in enumerate(boxes)
                  if _xov(ax0, ax1, b[0], b[2]) > 0 and _xov(ay0, ay1, b[1], b[3]) > 0]
            if not ov:
                orphans.append((ax0, ay0, ax1, ay1))
        # Round 20 track-p21: cluster orphan subs first — a light letter's core
        # fragments into thin pieces at 140 (p21 "a": bowl 13px + stem 3px, each
        # below the 0.5*med_h word-width guard, 3px apart). Merge orphans whose
        # x-gap is letter-scale (<= the pipeline word-gap floor) with y-overlap,
        # so the cluster — not the fragment — faces the word-like guards.
        # Two orphan letters of DIFFERENT words sit a word-gap apart and stay
        # separate, by the same discriminator the main pipeline uses.
        # Round 20 track-p21 v2: cluster fragments of ONE letter, which can be
        # side-by-side ("a" bowl+stem, 3px apart) OR stacked ("g" bowl over its
        # descender, y-gap 0). Either adjacency merges; two letters of different
        # words sit a word-gap apart in x (or a full line apart in y) and stay
        # separate. Single-linkage fixpoint (orphan counts are small).
        def _touch(a, b):
            _xgap = max(b[0] - a[2], a[0] - b[2])
            _ygap = max(b[1] - a[3], a[1] - b[3])
            _xov = min(a[2], b[2]) - max(a[0], b[0])
            _yov = min(a[3], b[3]) - max(a[1], b[1])
            return (_xgap <= max(8, 0.30 * med_h) and _yov > 0) or                (_ygap <= 2 and _xov > 0)
        _merged = list(orphans)
        _changed = True
        while _changed:
            _changed = False
            for _i in range(len(_merged)):
                for _j in range(_i + 1, len(_merged)):
                    if _touch(_merged[_i], _merged[_j]):
                        _a, _b = _merged[_i], _merged[_j]
                        _merged[_i] = (min(_a[0], _b[0]), min(_a[1], _b[1]),
                                       max(_a[2], _b[2]), max(_a[3], _b[3]))
                        del _merged[_j]
                        _changed = True
                        break
                if _changed:
                    break
        orphans = _merged
        n_orp = 0
        for (ax0, ay0, ax1, ay1) in orphans:
            wpx, hpx = ax1 - ax0, ay1 - ay0
            if wpx < 0.5 * med_h or wpx > 3.0 * med_h:
                continue
            if hpx > 2.5 * med_h:
                continue
            area = wpx * hpx
            if any(_xov(ax0, ax1, b[0], b[2]) * _xov(ay0, ay1, b[1], b[3]) > 0.5 * area
                   for b in boxes):
                continue  # mostly inside an existing word: part of it, not its own
            # Round 20 fix (Aug p1 "@", 2026-11-08): a single symbol sitting in
            # a word gap is not a dropped word. The "@" of "pgfoils@pgfoils.in"
            # sits 4px from "pgfoils" and 42px from "pgfoils.in" — letter-close
            # to one neighbour and far from the other, inside a word-gap span
            # (61px). A genuinely dropped word fills its slot: both gaps are
            # word-scale (p21 max 12px), or it sits at a line edge (one side
            # open). A layout gap (p09: 337px to the left word, span 358px) is
            # not a word gap — the orphan there is a real word at a section
            # start and is kept. So skip an orphan only when it has a word
            # neighbour on BOTH sides, one gap <= 0.5*med_h, the other
            # > 1.0*med_h, and the neighbour-to-neighbour span <= 3.0*med_h.
            # (Darkness does NOT separate it: the "@" is dark, IoU 0.93, but so
            # are 54 real reclaimed letters on p13/p14/p15 — IoU 1.00. The gap
            # position is the discriminator, not the ink.)
            _oh = ay1 - ay0
            _le = None; _rs = None
            for _b in boxes:
                if min(ay1, _b[3]) - max(ay0, _b[1]) <= 0.5 * _oh:
                    continue
                if _b[2] <= ax0 and (_le is None or _b[2] > _le):
                    _le = _b[2]
                elif _b[0] >= ax1 and (_rs is None or _b[0] < _rs):
                    _rs = _b[0]
            if _le is not None and _rs is not None:
                _lg, _rg = ax0 - _le, _rs - ax1
                if ((_lg <= 0.5 * med_h and _rg > 1.0 * med_h) or
                        (_rg <= 0.5 * med_h and _lg > 1.0 * med_h)) and \
                        (_rs - _le) <= 3.0 * med_h:
                    continue  # symbol in a word gap, not a dropped word
            out.append({"box": [ax0, ay0, ax1, ay1], "n_comp": 1, "src": "core-reclaim"})
            boxes.append([ax0, ay0, ax1, ay1])
            n_orp += 1
        if n_ext or n_orp:
            print(f"core-reclaim: extended {n_ext} boxes, +{n_orp} orphan words")
        return out, n_ext, n_orp


    def _f5_merge(groups):
        """300-DPI FIX F5, factored out (Round 22 FIX3): merge a lone narrow
        piece (spaced letter) into its neighbour. Used by _split_from_subs
        (outer grouping) and _split_light_print."""
        _mg = []
        for _g in groups:
            if len(_g) == 1 and _g[0][2] < 0.7 * med_h and _mg:
                _mg[-1].extend(_g)
            else:
                _mg.append(_g)
        if len(_mg) > 1 and len(_mg[0]) == 1 and _mg[0][0][2] < 0.7 * med_h:
            _mg[1] = _mg[0] + _mg[1]
            _mg = _mg[1:]
        return _mg


    def _split_from_subs(subs, x0, y0, subs_u, mult, ref_w, core_subs=None, core_subs_ext=None):
        """Group subs into word boxes (all-qualifying-gaps + F5) and validate:
        the old geometry/tot_w>=0.5 check (tot_w against ref_w: the blob width
        for a whole-blob split, the row's own span for a row split) AND
        _all_subs_accounted (Round 21 Track D E2: every uneroded sub covered by
        a word box or a gap mark; replaces the R19 0.92 threshold with no tuned
        fraction — the strict-1.0 attempt failed the fitz email split, see the
        validation comment below).
        Returns (words, ok).
        Round 20 track-p21: if core_subs are given, _reclaim_core runs AFTER
        validation, ONLY on a split that already passed (see the call site).
        Measuring first (p21 blob [1437,1328,2030,1359]) showed reclaim-BEFORE-
        validation backfires: it patched the coverage of a BAD eroded split
        (2 words for a 6-word line) so subcov passed and the retry never ran.
        Validation judges the split; reclaim repairs a validated split — it
        cannot un-merge an over-merge, so it must not vote on validity."""
        groups = _group_subs(subs, mult=mult)
        # ROUND 22 FIX3 (p21): wide-group LOCAL re-split — REMOVED 2026-11-09.
        # The re-split (_profile_resplit, deleted) fixed the p21 7-word
        # stretch (6/7 words, "ofexpiry" remaining) but MEASURED WRONG
        # everywhere else: it over-split SIX boxes across the corpus —
        # p01 email "mataplt@matagroup.in" into 6 fragments (+4 reclaim
        # orphans), p09/p12 codes "U1EX/2627/60023/DT.0" (split off "U" /
        # "U1"), p2 GSTIN "24AAACR7333J1ZE" into 3, p22
        # "DISCHARGEBDBNP" (merged label+value, isolated "P"), p3
        # "COMMERCIAL" into "COM"+"MERCIAL". The true word runs (7,9,10px
        # on p21) overlap the false letter runs (5,6,9px) in every gap/run
        # measure tried, and no multiplier separates them (1.5x cuts the
        # false ones; 1.75x is a knife-edge fitted to these 5 cases and is
        # rejected as threshold-fitting). One correct fix against six
        # regressions is not a fix. The p21 stretch therefore stays one
        # merged box (gate T3 1) — see TRACK-REPORT.md. A wide group is
        # still just F5-merged and validated as before.
        groups = _f5_merge(groups)
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
        ok = (len(words) >= 1 and tot_w >= 0.5 * ref_w
              and all((wd["box"][2] - wd["box"][0]) >= 0.5 * med_h
                      and (wd["box"][3] - wd["box"][1]) <= 2.5 * med_h for wd in words))
        if ok:
            # R19-2a: ink reconciliation — a split that drops a letter is a failed
            # split even if tot_w passes (erosion destroys letters: Ambawadi "wa").
            # R19-fix (Aug p1 email, 2026-11-08) — RESTORED by the Round 20 merge
            # (missing from the R20 tracks' pre-fix copy): == 1.0 is too strict for
            # email addresses — the "@" symbol sits in the word gap and its inner
            # part is covered by neither word box, so a CORRECT split scores 13/14 =
            # 0.929. Threshold 0.92 accepts it while still rejecting the diagnosed
            # bad Raviraj splits (Ambawadi 0.800, Ahmedabad 0.636, p21 0.639) AND the
            # p16-p19 header split (0.9091, 10/11 subs) which otherwise creates a
            # T1-flagged word [1924,396,1999,428] and flips those 4 pages ALLOW->REFUSE.
            # (0.90 was tried first and REGRESSED the gate 17/8 -> 13/12.)
            ok = _all_subs_accounted(subs_u, words, x0, y0)
        if ok and core_subs:
            # Round 20 track-p21: reclaim ONLY a validated split (see docstring).
            words, _n_ext, _n_orp = _reclaim_core(words, core_subs, x0, y0, core_subs_ext)
        return words, ok


    def _split_light_print(bbox):
        """Round 22 Track P20 — light-print fallback for split_blob_words.

        Root cause (measured on p20, 2026-11-09): the page's small print is
        LIGHT — ink median grey ~190-204, min ~112-155 — so the dark threshold
        (0.65*otsu = 141 at otsu 217) finds ZERO letter pieces in all 8 T3
        boxes and split_blob_words early-returns ([], 0): the v3 second-pass
        split never runs and the whole line stays one word box. The cause is
        NOT a rule/stamp bridging the words (measured: 0 straddling comps,
        gap columns are clean paper, mean grey 240-248, 0 Otsu ink; no row
        exceeds 0.90 ink) — it is the main grouping's 8px floor
        (max(8, 0.30*med_h)) against 5-8px word gaps on a med_h=14 page.

        Fallback (re-group the box's OWN pipeline comps, 8-connected Otsu,
        area>=14 — the exact units the main grouping joined):
          * v1 used the dark-sub extractor (4-connected, area>=34) on the
            Otsu mask instead: MEASURED WRONG on p20 (2026-11-09) — the
            area floor drops small light-print letter fragments, leaving
            PHANTOM gaps up to 20px that become false word cuts (#2 REGN:
            5 pieces for GT 3; #0 DILKUSHA cut in two). The pipeline comps
            keep every fragment, so no phantom gap can appear.
          * UNIFORM-SPACING GUARD (FIX3, Round 22): the R22 guard fired on
            uniformity alone — MEASURED WRONG (2026-11-09): when letters
            fuse into word-sized pieces, the gaps BETWEEN words are the only
            gaps left and they are uniform too, so the guard protected real
            collapses ("58 DILKUSHA", "MARKS & NOS", "VESSEL / TRUCK",
            "OF ORIGIN"). It now fires only when the gaps are LETTER gaps:
            uniform AND max gap < 0.30 x the pieces' OWN median height
            (0.30 = the pipeline's V4-4 constant; the box's own height is
            the ruler because the box's font can differ from the page
            median — the 37px CONSIGNOR caps on a med_h=20 page).
            Measured: singles <= 0.22x, collapses >= 0.27x (13 eye-verified
            light boxes).
          * cut at a CC gap >= max(5, 0.30*med_h) (FIX3, Round 22) whose
            Otsu column profile ALSO has a zero-run >= 3px overlapping the
            gap: a CC gap is a proxy for empty space and fails when pieces
            overlap (BENAPOLE's 7px CC gap has ink in its columns; its 4px
            CC gap is a clean run). Same mask as the rhythm DP. The
            threshold is the pipeline's own V4-4 word-gap constant, NOT a
            fixed 5px: MEASURED WRONG (2026-11-09) — a fixed 5px cut SHREDS
            the letterspaced blue address lines on med_h=26 pages (p07
            email "info@ravirajfoils.com," split into 8 pieces; p07-p12
            gained +32..+47 phantom words), because letter gaps there reach
            7px. The old CC-gap cut's max(5, 0.30*med_h) was load-bearing
            for exactly this reason. And a pure column-run cut (run >= 5)
            is MEASURED WRONG the other way: stray specks (area 4-9)
            break the run at real word gaps and MERGED four correct
            baseline splits on p20 ("EIGHTY NINE", an invoice date +
            token, an A/C number pair, a bottom-line pair), whose Otsu
            runs are only 3-4px — so the run test is a "mostly empty"
            veto (>= 3px, the smallest recognised separation) on top of
            the CC-gap test, not a replacement for it. BENAPOLE's gap has
            only a 2px empty run, so it stays whole. Margin 1px — see
            TRACK-REPORT.md.
          * Plus standalone-symbol isolation (p01 "today @ Rs.": the @ is
            one letter-sized comp with gaps 3 and 5 on its sides) and
            rule-attach (a flat long comp never starts a group).
          * F5 lone-narrow-piece merge + the same validation as
            _split_from_subs (tot_w, word geometry, _all_subs_accounted).
        NOT the rhythm DP: on light print the dark profile is empty, so the
        DP's clear_run=4 cuts at 4px letter gaps (measured p20 #2: DP 6
        words for GT 3; #0: a false cut inside ISLAMI). A failed light
        split returns [] (keep the whole box), never DP.
        Returns (words, n_subs) like split_blob_words."""
        x0, y0, x1, y1 = bbox
        # The box's own pipeline comps: Otsu CCs (labels/stats globals) with
        # the pipeline's own comp filters, centre inside the box.
        subs_o = []
        for i in range(1, num):
            cx, cy, ww, hh, area = (int(v) for v in stats[i])
            if area < 14:
                continue
            if (ww > 375 and hh <= 15) or (hh > 150 and ww <= 15):
                continue
            if ww > 900 or hh > 180:
                continue
            if in_excluded(cx, cy, ww, hh):
                continue
            if ww >= 120 and hh >= 23 and area / (ww * hh) <= 0.20 \
                    and _edge_frac({"x": cx, "y": cy, "w": ww, "h": hh,
                                    "lab": i}) >= 0.40:
                continue  # hollow border/frame, as in the main comp filter
            ccx, ccy = cx + ww / 2, cy + hh / 2
            if not (x0 <= ccx <= x1 and y0 <= ccy <= y1):
                continue
            if ccy >= sig_y:
                continue
            # Enclosed counters (holes) of this comp, from the Otsu label
            # image: needed by the standalone-symbol test below. A comp's
            # own mask is (labels == i) inside its bbox; RETR_CCOMP gives
            # each hole as a contour with a parent.
            _m = (labels[cy:cy + hh, cx:cx + ww] == i).astype(np.uint8)
            _cn, _hi = cv2.findContours(_m, cv2.RETR_CCOMP,
                                         cv2.CHAIN_APPROX_SIMPLE)
            _holes = int((_hi[0][:, 3] != -1).sum()) if _hi is not None else 0
            # Bbox-RELATIVE coords (like _extract_subs): word boxes below are
            # built as x0 + min(...) and _all_subs_accounted adds (x0, y0).
            # 5th element = enclosed-counter count (holes) for the symbol test.
            subs_o.append((cx - x0, cy - y0, ww, hh, _holes))
        subs_o.sort(key=lambda s: s[0])
        import os as _osdbg4
        if _osdbg4.environ.get("FIX3_DEBUG"):
            _g4 = []
            _r4 = subs_o[0][0] + subs_o[0][2] if subs_o else 0
            for _c in subs_o[1:]:
                _g4.append(_c[0] - _r4); _r4 = max(_r4, _c[0] + _c[2])
            print(f"FIX3DBG light-print {list(bbox)} med_h={med_h} nsubs_o={len(subs_o)} subs={subs_o} gaps={_g4}")
        if len(subs_o) < 2:
            return [], len(subs_o)
        gaps, rmax = [], subs_o[0][0] + subs_o[0][2]
        for c in subs_o[1:]:
            gaps.append(c[0] - rmax)
            rmax = max(rmax, c[0] + c[2])
        pos = [g for g in gaps if g > 0]
        if not pos:
            return [], len(subs_o)
        # ROUND 22 FIX3 (p20): SCALE-AWARE uniform-spacing guard. Uniformity
        # alone cannot tell a letterspaced word from fused words: when the
        # letters fuse into word-sized pieces, the gaps BETWEEN words are the
        # only gaps left, and they are uniform too (measured: the guard
        # wrongly protected real collapses "58 DILKUSHA", "MARKS & NOS",
        # "VESSEL / TRUCK", "OF ORIGIN" — all with uniform gaps). The guard
        # may only fire when the gaps are LETTER gaps, i.e. small against the
        # pieces' OWN height: max(pos) < 0.30 * med_piece_h, where 0.30 is
        # the pipeline's own word-gap constant (V4-4) and med_piece_h is the
        # box's own letter height (the page median is the wrong ruler when
        # the box's font differs from the page's, e.g. the 37px red
        # CONSIGNOR caps on a med_h=20 page). Measured separation on 13
        # eye-verified light boxes: single words max gap <= 0.22*piece_h
        # (NARAYANGANJ, PLYWOOD, CONSIGNOR x2, p07 blue); collapses
        # >= 0.27*piece_h (DHAKA 0.38+, VESSEL, MARKS, OF ORIGIN, DATEOF,
        # 58 DILKUSHA, BENAPOLE). The 0.30 constant sits in the gap.
        _hs = sorted(s[3] for s in subs_o)
        _med_piece_h = _hs[len(_hs) // 2]
        if min(pos) > 0.5 * max(pos) and max(pos) < 0.30 * _med_piece_h:
            print(f"light-print split {list(bbox)}: uniform gaps "
                  f"{sorted(gaps)} (min/max {min(pos)}/{max(pos)}, "
                  f"max {max(pos) / _med_piece_h:.2f}x piece_h) -> one "
                  f"word, no split")
            return [], len(subs_o)
        # ROUND 22 FIX3: COLUMN-RUN cuts (p20 BENAPOLE) + standalone-symbol
        # isolation (p01 @). A CC gap is a proxy for empty space and fails
        # when pieces overlap: BENAPOLE's 7px CC gap has ink in its columns
        # (overlapping pieces), so it is NOT empty space, while its 4px CC
        # gap IS a clean 6px column run. Cut only where the Otsu column
        # profile (same mask the DP uses, rule rows stripped as there) has a
        # zero-run >= 5px overlapping the CC gap — 5px is the existing floor,
        # no new constant. A run < 5px (e.g. a 4px letter gap) never cuts.
        # Rule-like comps (flat and long: h <= 0.30*med_h, w >= 3*med_h —
        # the p01 underline, 132x4) never start a group: they attach to the
        # previous group, so a rule can neither become a word nor be split
        # off its line (the DP made exactly that rule-word on p01).
        # Standalone symbols (p01 @): a single letter-sized comp
        # (0.4*med_h <= w <= 2.0*med_h, 0.5*med_h <= h <= 2.0*med_h) with
        # clear space on BOTH sides — the smaller gap >= 3px (above the
        # letter-gap scale measured on the line: 0-2px) and the larger
        # ROUND 22 FIX3: COLUMN-RUN cuts (p20 BENAPOLE) + standalone-symbol
        # isolation (p01 @). A CC gap is a proxy for empty space and fails
        # when pieces overlap: BENAPOLE's 7px CC gap has ink in its columns
        # (a 5px serif fragment of the "L"/"E" at the baseline), so it is
        # NOT empty space, while its 4px CC gap is a clean run. Cut only
        # where BOTH hold: the CC gap itself is >= max(5, 0.30*med_h) (the
        # pipeline's own V4-4 threshold — see docstring: a fixed 5px cut
        # shreds the letterspaced blue address lines on med_h=26 pages)
        # AND the Otsu column profile (same mask the DP uses, rule rows
        # stripped as there) has a zero-run >= 3px overlapping the gap.
        # The run test is a "mostly empty" veto, not a "fully empty" one:
        # MEASURED (2026-11-09) — a pure column-run cut (run >= 5) is
        # TOO STRICT: stray specks (area 4-9, below the comp floor) break
        # the run at real word gaps and MERGED four correct baseline
        # splits on p20 ("EIGHTY NINE", an invoice date + token, an A/C
        # number pair, a bottom-line pair), whose Otsu runs are only 3-4px.
        # The 3px floor is the smallest space the pipeline recognises as a
        # separation (the isolation rule's smaller-gap floor, below);
        # BENAPOLE's gap has only a 2px empty run, so it stays whole.
        # Margin is 1px (2 vs 3) — reported honestly in TRACK-REPORT.md.
        # A run below the floor (e.g. a 4px letter gap) never cuts.
        # Rule-like comps (flat and long: h <= 0.30*med_h, w >= 3*med_h —
        # the p01 underline, 132x4) never start a group: they attach to the
        # previous group, so a rule can neither become a word nor be split
        # off its line (the DP made exactly that rule-word on p01).
        # Standalone symbols (p01 @): a single letter-sized comp
        # (0.4*med_h <= w <= 2.0*med_h, 0.5*med_h <= h <= 2.0*med_h) with
        # clear space on BOTH sides — the smaller gap >= 3px (above the
        # letter-gap scale measured on the line: 0-2px) and the larger
        # gap >= 5px (the existing floor) — AND >= 4 enclosed counters
        # (holes). The holes test is what makes the rule a SYMBOL test
        # rather than a letter-group test: MEASURED (2026-11-09) on every
        # isolation firing across p01/p20 — the @ has 5 holes; every other
        # firing (35 of them: spaced letters on p07-p12, DI/LK inside
        # DILKUSHA, fused 2-3-letter groups) has 0-3 (next highest is a
        # fused 3-letter group with 3). A multi-loop glyph like @ is the
        # only common letter-sized comp with >= 4 enclosed counters; plain
        # letters have 0-1, "8"/"B" have 2, fused pairs reach 3.
        _col_thr = max(5, 0.30 * med_h)
        _crop = gray[y0:y1, x0:x1]
        _oink = _crop < otsu_val
        _row_ink = _oink.sum(axis=1)
        _keep = _row_ink <= 0.90 * (x1 - x0)
        _po = (_oink & _keep[:, None]).sum(axis=0)
        _runs = []
        _s = None
        for _i, _v in enumerate(_po):
            if _v == 0 and _s is None:
                _s = _i
            elif _v != 0 and _s is not None:
                _runs.append((_s, _i, _i - _s)); _s = None
        if _s is not None:
            _runs.append((_s, len(_po), len(_po) - _s))

        def _clean(_a, _b):
            # longest zero-run overlapping the column span [_a, _b)
            _best = 0
            for (_rs, _re, _rl) in _runs:
                _ov = min(_re, _b) - max(_rs, _a)
                if _ov > 0:
                    _best = max(_best, _ov)
            return _best
        _cuts = set()
        _right = subs_o[0][0] + subs_o[0][2]
        for _i, _c in enumerate(subs_o[1:]):
            _span_a, _span_b = _right, _c[0]
            _gap = _span_b - _span_a
            if _gap >= _col_thr and _clean(_span_a, _span_b) >= 3:
                _cuts.add(_i)
            _right = max(_right, _c[0] + _c[2])
        # standalone-symbol isolation
        _iso = set()
        for _j in range(1, len(subs_o) - 1):
            _sx, _sy, _sw, _sh = subs_o[_j][:4]
            if not (0.4 * med_h <= _sw <= 2.0 * med_h
                    and 0.5 * med_h <= _sh <= 2.0 * med_h):
                continue
            if subs_o[_j][4] < 4:
                continue  # not a multi-loop symbol (see above)
            _lg, _rg = gaps[_j - 1], gaps[_j]
            if _lg > 0 and _rg > 0 and min(_lg, _rg) >= 3 and max(_lg, _rg) >= 5:
                _iso.add(_j)
                _cuts.add(_j - 1)
                _cuts.add(_j)
        # rule-like comps attach to the previous group (never start one)
        for _j in range(1, len(subs_o)):
            if subs_o[_j][3] <= 0.30 * med_h and subs_o[_j][2] >= 3.0 * med_h:
                _cuts.discard(_j - 1)
                _iso.discard(_j)
        if _iso:
            print(f"light-print split {list(bbox)}: standalone symbol(s) "
                  f"at comp idx {sorted(_iso)}")
        if not _cuts:
            return [], len(subs_o)
        groups, cur = [], [subs_o[0]]
        for i, c in enumerate(subs_o[1:]):
            if i in _cuts:
                groups.append(cur)
                cur = [c]
            else:
                cur.append(c)
        groups.append(cur)
        # F5 (same as _split_from_subs): merge a lone narrow piece into its neighbour.
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
            words.append({"box": [wx0, wy0, wx1, wy1], "n_comp": len(g),
                          "src": "light-split"})
        tot_w = sum(wd["box"][2] - wd["box"][0] for wd in words)
        ok = (len(words) >= 2 and tot_w >= 0.5 * (x1 - x0)
              and all((wd["box"][2] - wd["box"][0]) >= 0.5 * med_h
                      and (wd["box"][3] - wd["box"][1]) <= 2.5 * med_h
                      for wd in words)
              and _all_subs_accounted(subs_o, words, x0, y0))
        if not ok:
            return [], len(subs_o)
        print(f"light-print split {list(bbox)} -> {len(words)} words "
              f"({len(subs_o)} pieces, {len(_cuts)} cuts)")
        return words, len(subs_o)


    # --- ROUND 26 TRACK-TAU: US 20150086113 tau-signal fused-line split ----
    # Patent (Tata Consultancy, publ. 26 Mar 2015): per column of a binarised
    # component, cnt_txt = text pixels in the column, longest_txt = longest
    # continuous text run in the column, tau_i = cnt_txt * longest_txt. A
    # column is a candidate cut iff tau_{i+1} > tau_i <= tau_{i-1} and
    # tau_i < threshold (threshold "heuristic", example 10 for Indian TV).
    #
    # MEASURED on p21's stretch [827,1970,1317,2005] (pipeline render, page
    # Otsu 184): the 6 true boundaries are literally empty columns (tau 0)
    # while EVERY intra-word column has tau >= 28 (min false local-minimum
    # tau = 32). EVERY integer threshold T in [1, 32] gives 6/6 hits + 0
    # false cuts; T=1 is the conservative endpoint (cut only where the column
    # is literally empty), NOT a fitted value. Pieces recover 7/7 words at
    # +-3px and +-5px. The same 6/6 holds at thr 183/185/crop-Otsu and on the
    # round4 render (at T=2 there). On p20's fused line tau is INVERTED
    # (true tau 144/196/144 vs intra max 70; 0/4 words at EVERY threshold),
    # so tau must NEVER fire there.
    #
    # GUARD (faithful port of the gate's T3 Path B decision, gate_merged.py
    # collapse_candidates): the gate's own eye decides "this box is a
    # collapse of 2+ words"; tau only decides WHERE to cut inside it.
    #   (a) width >= 12x med_h, height in (0.35, 2.5]x med_h, not rule-shaped
    #   (b) the box's Otsu CCs, split at gaps >= thr = max(5, 1.70 x
    #       trim_med) [trim_med = median gap excluding the 2 largest],
    #       yield >= 2 word-like groups (n_cc>=2 and w>=20px, or one CC
    #       w>=2.5x med_h); hyphen-adjacent gaps never split
    #   (c) no tight joiner (phone/email/URL punctuation with gaps < thr on
    #       both sides)
    # On the 33-page corpus the gate flags exactly TWO boxes (p20 Path C,
    # p21 Path B); this guard fires on p21 only — p20's 3 fused CCs give
    # 1 group (n_wl=1), so tau never touches p20. An UNSCOPED tau(T=1)
    # would shred genuine words (measured: 14 false cuts in 8 p20/p21
    # words, 36 in 12 p01 words, 40 in 12 p12 words, 51 in 12 Aug-p1-fitz
    # words) — the guard is what makes this promotable, not the signal.
    # SIMPLIFICATION (documented): the gate's <=2-gaps fallback
    # thr = max(5, 1.5 x line_med) needs the line's letter-gap median,
    # which split_blob_words does not see; the segmenter uses the 5px
    # floor. line_med is 1-2px on these pages, so max(5, 1.5xline_med) = 5
    # there; any divergence shows up as an unexpected seg change in the
    # 33-page diff, which is checked.
    _TAU_MIN_W_MED = 12.0
    _TAU_MIN_H_MED = 0.35
    _TAU_MAX_H_MED = 2.5
    _TAU_SPLIT_FACTOR = 1.70
    _TAU_SPLIT_FLOOR_PX = 5
    _TAU_WORD_MIN_W_PX = 20
    _TAU_FUSED_WORD_MIN_W_MED = 2.5
    _TAU_CUT = 1  # patent tau_i < threshold; 1 = cut only at tau == 0
    _TAU_MIN_PIECE_MED = 0.5  # piece width floor (seam's rule)


    def _tau_is_rule_shaped(cw, ch, area):
        """Copied verbatim from gate_merged.py is_rule_shaped."""
        fill = area / max(1, cw * ch)
        return ((cw >= 150 and ch <= 10) or (ch >= 150 and cw <= 10)
                or (max(cw, ch) >= 150 and fill < 0.20))


    def _tau_box_ccs(box):
        """Page Otsu CCs (gate recipe: area>=4) whose centre lies inside the
        box, in x order, as (x0, x1, y0, y1, w, h, fill, holes). Reuses the
        pipeline's own connected-components stats (same image, same Otsu)."""
        x0, y0, x1, y1 = box
        iv = []
        for s in stats[1:]:
            cx, cy, cw, ch, a = (int(v) for v in s)
            if a < 4:
                continue
            if x0 <= cx + cw / 2 <= x1 and y0 <= cy + ch / 2 <= y1:
                iv.append((cx, cx + cw, cy, cy + ch, cw, ch,
                           a / max(1, cw * ch), 0))
        iv.sort(key=lambda t: t[0])
        return iv


    def _tau_holes_for(iv):
        """Enclosed-hole count per box CC (gate _cc_holes_for_t3, but only
        for the CCs in this box). Keyed by (x, y, w, h). The component id
        is recovered by matching the stats bbox (the centre pixel can be
        background in a hollow glyph)."""
        out = {}
        for (x0, x1, y0, y1, w, h, _fill, _ho) in iv:
            lab_id = None
            for _lid in np.unique(labels[y0:y1, x0:x1]):
                if _lid <= 0:
                    continue
                _s = stats[int(_lid)]
                if (int(_s[0]), int(_s[1]), int(_s[2]), int(_s[3])) == (x0, y0, w, h):
                    lab_id = int(_lid)
                    break
            if lab_id is None:
                out[(x0, y0, w, h)] = 0
                continue
            m = (labels[y0:y1, x0:x1] == lab_id).astype("uint8")
            cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP,
                                          cv2.CHAIN_APPROX_SIMPLE)
            out[(x0, y0, w, h)] = int((hier[0][:, 3] != -1).sum()) \
                if hier is not None else 0
        return out


    def _tau_nonneg_gaps(iv):
        """Non-negative x-gaps between consecutive CCs (running right edge);
        overlapping (negative) gaps are ink fusion, not a space (gate)."""
        gaps = []
        if len(iv) < 2:
            return gaps
        right = iv[0][1]
        for t in iv[1:]:
            gaps.append(t[0] - right)
            right = max(right, t[1])
        return [gp for gp in gaps if gp >= 0]


    def _tau_trim_med(gaps):
        """Median gap excluding the 2 largest (the word gaps themselves).
        None when <= 2 gaps (gate)."""
        if len(gaps) <= 2:
            return None
        rest = sorted(gaps)[:-2]
        return float(np.median(rest))


    def _tau_split_groups(iv, med_h, thr):
        """Split the box's CCs at gaps >= thr (gate _split_groups_t3).
        Hyphen-adjacent gaps never split. Returns (groups, n_word_like)."""
        if not iv:
            return [], 0
        groups = []
        cur = [iv[0]]
        for k in range(1, len(iv)):
            prev, nxt = iv[k - 1], iv[k]
            gap = nxt[0] - max(t[1] for t in cur)
            hy = (prev[5] < 0.55 * med_h and prev[4] >= 1.5 * prev[5]
                  and prev[4] >= 0.4 * med_h) or \
                 (nxt[5] < 0.55 * med_h and nxt[4] >= 1.5 * nxt[5]
                  and nxt[4] >= 0.4 * med_h)
            if gap >= thr and not hy:
                groups.append(cur)
                cur = [nxt]
            else:
                cur.append(nxt)
        groups.append(cur)
        n_wl = 0
        for gr in groups:
            w = max(t[1] for t in gr) - gr[0][0]
            if (len(gr) >= 2 and w >= _TAU_WORD_MIN_W_PX) or \
               (len(gr) == 1 and w >= _TAU_FUSED_WORD_MIN_W_MED * med_h):
                n_wl += 1
        return groups, n_wl


    def _tau_is_hyphen_like(c, med_h, band_c):
        return (c[5] < 0.55 * med_h and c[4] >= 1.5 * c[5]
                and c[4] >= 0.4 * med_h
                and abs((c[2] + c[3]) / 2 - band_c) <= 0.25 * med_h)


    def _tau_is_slash_like(c, med_h):
        return (c[5] >= 0.8 * med_h and c[4] <= 0.5 * med_h
                and c[6] <= 0.30)


    def _tau_is_at_like(c, med_h):
        return (c[5] >= 1.5 * med_h
                and 1.5 * med_h <= c[4] <= 2.5 * med_h
                and 1 <= c[7] <= 2)


    def _tau_has_tight_joiner(iv, med_h, band_c, thr):
        """Gate _has_tight_joiner_t3 verbatim in logic."""
        if len(iv) < 3:
            return False
        for k in range(1, len(iv) - 1):
            c = iv[k]
            left_gap = c[0] - max(t[1] for t in iv[:k])
            right_gap = iv[k + 1][0] - c[1]
            if not (0 <= left_gap < thr and 0 <= right_gap < thr):
                continue
            if _tau_is_hyphen_like(c, med_h, band_c):
                return True
            if _tau_is_slash_like(c, med_h):
                return True
            if _tau_is_at_like(c, med_h):
                return True
        return False


    def _tau_profile(binary):
        """binary: boolean (H, W), True = text pixel. Returns
        (cnt, longest, tau) per column, tau = cnt * longest (patent)."""
        H, W = binary.shape
        cnt = binary.sum(axis=0).astype(int)
        longest = np.zeros(W, dtype=int)
        for j in range(W):
            best = cur = 0
            for v in binary[:, j]:
                cur = cur + 1 if v else 0
                best = max(best, cur)
            longest[j] = best
        return cnt, longest, cnt * longest


    def _split_fused_tau(bbox):
        """Round 26 track-tau: split a gate-T3-Path-B collapse with the
        patent tau rule (cut only at tau == 0 columns). Returns (words,
        n_ccs) like split_blob_words, or ([], n_ccs) when the guard fails
        or no valid cut set exists — the caller then keeps the whole word
        box, exactly as before."""
        x0, y0, x1, y1 = bbox
        wpx, hpx = x1 - x0, y1 - y0
        # (a) legs — the gate never examines other boxes.
        if wpx < _TAU_MIN_W_MED * med_h:
            return [], 0
        if not (_TAU_MIN_H_MED * med_h < hpx <= _TAU_MAX_H_MED * med_h):
            return [], 0
        if _tau_is_rule_shaped(wpx, hpx, wpx * hpx):
            return [], 0
        iv = _tau_box_ccs(bbox)
        if len(iv) < 2:
            return [], len(iv)
        holes = _tau_holes_for(iv)
        iv = [(t[0], t[1], t[2], t[3], t[4], t[5], t[6],
               holes.get((t[0], t[2], t[4], t[5]), 0)) for t in iv]
        gaps = _tau_nonneg_gaps(iv)
        trim = _tau_trim_med(gaps)
        thr = max(_TAU_SPLIT_FLOOR_PX, _TAU_SPLIT_FACTOR * trim) \
            if trim is not None else float(_TAU_SPLIT_FLOOR_PX)
        _groups, n_wl = _tau_split_groups(iv, med_h, thr)
        print(f"fused-tau guard {list(bbox)}: {len(iv)} CCs, gaps={gaps}, "
              f"trim={trim}, thr={thr:.1f}, n_word_like={n_wl}")
        if n_wl < 2:
            return [], len(iv)
        band_c = (y0 + y1) / 2
        if _tau_has_tight_joiner(iv, med_h, band_c, thr):
            print(f"fused-tau guard {list(bbox)}: tight joiner -> keep whole box")
            return [], len(iv)
        # Cutter: patent tau rule, threshold 1 (tau == 0 only).
        binary = gray[y0:y1, x0:x1] < otsu_val
        _cnt, _longest, tau = _tau_profile(binary)
        cuts = [i for i in range(1, len(tau) - 1)
                if tau[i + 1] > tau[i] <= tau[i - 1] and tau[i] < _TAU_CUT]
        if not cuts:
            print(f"fused-tau split {list(bbox)}: guard passed but no tau==0 "
                  f"local minima -> keep whole box")
            return [], len(iv)
        edges = [x0] + [x0 + c + 1 for c in cuts] + [x1]
        words = []
        for _a, _b in zip(edges, edges[1:]):
            if _b - _a < _TAU_MIN_PIECE_MED * med_h:
                print(f"fused-tau split {list(bbox)}: piece {_a}-{_b} narrower "
                      f"than 0.5*med_h -> keep whole box")
                return [], len(iv)
            words.append({"box": [int(_a), y0, int(_b), y1], "n_comp": len(iv),
                          "src": "fused-tau"})
        if len(words) < 2:
            return [], len(iv)
        print(f"fused-tau split {list(bbox)} -> {len(words)} words "
              f"({len(iv)} CCs, thr={thr:.1f}, tau cuts rel {cuts}, "
              f"tau at cuts {[int(tau[c]) for c in cuts]})")
        return words, len(iv)


    def _tau_resplit_products(words):
        """Round 26 track-tau: a top2a/DP split can return a piece that is
        itself still a collapse — p21's stretch [827,1970,1317,2005] arrives
        as ONE piece of its parent blob's uneroded-retry split, so the
        end-of-function hook never sees it. Re-split any returned piece
        that passes the Path-B guard with the tau cutter; keep the rest
        unchanged. The guard (not this helper) is what protects genuine
        words: it fires on exactly 1 box in the corpus."""
        out = []
        for w in words:
            _tw, _tn = _split_fused_tau(tuple(w["box"]))
            if _tw:
                for p in _tw:
                    _nw = dict(w)
                    _nw.update({"box": p["box"], "n_comp": p["n_comp"],
                                "src": "fused-tau"})
                    out.append(_nw)
            else:
                out.append(w)
        return out
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
        subs_u = _extract_subs(ink)
        if not subs_u:
            # Round 22 Track P20: light print — no dark-ink letter pieces at
            # all (see _split_light_print). Fall back to the Otsu-level split,
            # NOT to the rhythm DP below (its dark profile is empty here).
            return _split_light_print(bbox)
        # Round 20 track-p21 (b): dark-core subs at the gate's CORE_THR (140),
        # for the reclaim check in _split_from_subs (grouping still uses dark).
        _core_ink = gray[y0:y1, x0:x1] < 140
        _core_row = _core_ink.sum(axis=1)
        _core_ink = _core_ink.copy()
        _core_ink[_core_row > 0.90 * _core_ink.shape[1], :] = False
        core_subs = _extract_subs(_core_ink, area_floor=20, h_floor=0.25)
        # Round 20 IoU fix: eroded copy of the 140-subs for the reclaim EXTENSION
        # only (tight to the letter core; breaks underline/halftone bridges).
        # Orphans still use the original core_subs (see _reclaim_core).
        core_subs_ext = _extract_subs(cv2.erode(_core_ink.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool), area_floor=20, h_floor=0.25)
        # V4-6 erosion fallback: in B&W the halftone dither bridges bold letters
        # into one wide piece. A 3x3 erosion breaks 1px bridges; letters survive.
        # Trigger: any sub wider than 2.5*med_h, or any negative (overlapping) gap.
        # Use the eroded subs only if they are plausibly letters.
        subs = subs_u
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
        words, ok = _split_from_subs(subs, x0, y0, subs_u, mult=1.5 if _eroded else 2.0,
                                     ref_w=(x1 - x0), core_subs=core_subs,
                                     core_subs_ext=core_subs_ext)
        if ok:
            # ROUND 26 TRACK-TAU: a returned piece can itself still be a
            # collapse (p21's stretch arrives as one piece of its parent
            # blob's split) — re-split such pieces with tau (guarded).
            return _tau_resplit_products(words), len(subs)
        # R19-2a retry: erosion destroyed letters (the hole it leaves becomes a
        # cut boundary). Retry with the UNERODED subs — bridged pieces collapse
        # via F5 into a whole-word box, which is correct for single-token blobs
        # (Ambawadi, pgfoils@pgfoils.in) and gate-clean. If the retry also fails,
        # return [] as before (v3 path keeps the whole word box; singleton drops).
        if _eroded:
            words2, ok2 = _split_from_subs(subs_u, x0, y0, subs_u, mult=2.0,
                                           ref_w=(x1 - x0), core_subs=core_subs,
                                           core_subs_ext=core_subs_ext)
            if ok2:
                print(f"blob-split retry (uneroded): {list(bbox)} -> {len(words2)} words")
                # ROUND 26 TRACK-TAU: re-split any still-collapsed piece.
                return _tau_resplit_products(words2), len(subs_u)
        # --- Round 19 merge: Rhythm-DP rescue (track-top2b), AFTER the top2a
        # validated split + uneroded retry both failed. top2b fired DP when
        # TOP-2 coverage < 0.90; here the top2a path already covers everything
        # subcov-valid, so DP fires exactly when top2a fails outright (the
        # gapless remainder gets 100% span coverage by construction).
        if _rhythm_dp_words is not None:
            try:
                _dp_words, _dbg = _rhythm_dp_words(
                    (x0, y0, x1, y1), gray, otsu_val, med_h, PITCH)
                _widths_ok = all((w["box"][2] - w["box"][0]) >= 8 for w in _dp_words)
                _interior_ok = all((w["box"][2] - w["box"][0]) >= 0.5 * med_h
                                   for w in _dp_words[1:-1])
                _sane = (len(_dp_words) >= 1 and _dbg["n_forced"] >= 2
                         and _widths_ok and _interior_ok)
                if _sane:
                    print(f"rhythm-dp blob {[x0, y0, x1, y1]}: top2a failed -> {len(_dp_words)} words (forced={_dbg['n_forced']})")
                    # ROUND 26 TRACK-TAU: re-split any still-collapsed piece.
                    return _tau_resplit_products(_dp_words), len(subs)
                print(f"rhythm-dp blob {[x0, y0, x1, y1]}: DP rejected (forced={_dbg['n_forced']}, n={len(_dp_words)}) -> []")
            except Exception as _e:
                print(f"rhythm-dp blob {[x0, y0, x1, y1]}: error {_e} -> []")
        # --- ROUND 26 TRACK-TAU: after top2a + retry + rhythm-DP all failed,
        # try the tau-signal split (guarded to gate-T3-Path-B collapses
        # only). It returns [] unless the guard + validation pass, so the
        # caller keeps the whole word box exactly as before on failure.
        _tw, _tn = _split_fused_tau(bbox)
        if _tw:
            return _tw, _tn
        return [], len(subs_u)

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
                              "n_comp": wd["n_comp"], "src": wd.get("src", "blob-split")})
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
                 if wd.get("src") in ("blob-split", "rhythm-dp", "core-reclaim") or not any(
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


    def _cluster_rows(subs, row_gap):
        """Cluster subs into rows by y-centre (chain gap row_gap). Returns a list
        of rows (each a list of subs) and the rows' mean y-centres.
        Round 21 track-p01 FIX (2026-11-08): the chain compares each sub to the
        PREVIOUS sub's centre (single-linkage), NOT to the row's running mean.
        The running mean LAGS when one text line's fragments walk down a tall
        glyph: on the p01 tagline "Nothing's" (light ink, dark subs cy 280.5 ->
        305.0, consecutive gaps all <= 8.5 < row_gap 12) the mean stayed behind
        the chain and cut ONE line into two rows (means 289.4 / 303.2); the two
        row-products then overlapped 56% and F3 dropped the upper one, clipping
        the "N" (gate T1 0.554). A row is a CHAIN of nearby centres, not a ball
        around a mean: if every consecutive step is <= row_gap, the subs are
        one row. This matches the pipeline's own chaining convention elsewhere
        (tall-stroke clusters chain on the last element; _group_subs cuts on
        consecutive gaps). Measured on all 7 successful row-splits in the
        33-page corpus: the 5 genuine multi-line blobs keep identical row
        counts (5/5/4/7/5), only the two bogus tagline splits (p01, canonical
        p2) collapse 2 -> 1 row. Single-linkage can only MERGE rows relative
        to the mean rule (a consecutive gap > row_gap also exceeds the mean
        distance), so no split can gain a row from this change."""
        _cy = lambda s: s[1] + s[3] / 2
        _by_cy = sorted(subs, key=_cy)
        rows, _cur = [], [_by_cy[0]]
        for _s in _by_cy[1:]:
            if _cy(_s) - _cy(_cur[-1]) <= row_gap:
                _cur.append(_s)
            else:
                rows.append(_cur)
                _cur = [_s]
        rows.append(_cur)
        means = [sum(_cy(t) for t in r) / len(r) for r in rows]
        return rows, means


    def _row_split_blob(bbox):
        """Round 19 Track 2a — split a TALL merged blob into per-row word boxes.
        Rows are clustered from the UNERODED subs (y-centre chain gap
        max(9, 0.6*med_h), the main pipeline's line-grouping constant); the
        split subs (eroded when the fallback fired) are assigned to the nearest
        row by y-centre. Each row is split with _split_from_subs (all-cuts + F5
        + subcov validation against the row's own uneroded subs, tot_w against
        the row's own span). If any row fails validation, or fewer than 2 rows /
        2 words result, returns ([], n) so the caller keeps the whole word box
        exactly as before."""
        x0, y0, x1, y1 = bbox
        dark = int(0.65 * otsu_val)
        if dark < 64:
            dark = 128
        ink = gray[y0:y1, x0:x1] < dark
        row_ink = ink.sum(axis=1)
        ink = ink.copy()
        ink[row_ink > 0.90 * ink.shape[1], :] = False
        subs_u = _extract_subs(ink)
        if len(subs_u) < 2:
            return [], len(subs_u)
        subs = subs_u
        _maxw = max((s[2] for s in subs), default=0)
        _gaps0 = []
        _rm = subs[0][0] + subs[0][2]
        for _c in subs[1:]:
            _gaps0.append(_c[0] - _rm)
            _rm = max(_rm, _c[0] + _c[2])
        _eroded = False
        if _maxw > 2.5 * med_h or min(_gaps0, default=0) < 0:
            ero = cv2.erode(ink.astype(np.uint8), np.ones((3, 3), np.uint8))
            subs_e = _extract_subs(ero)
            _maxw_e = max((s[2] for s in subs_e), default=0)
            if len(subs_e) >= 2 and _maxw_e <= 2.5 * med_h:
                subs = subs_e
                _eroded = True
        _row_gap = max(9, 0.6 * med_h)
        rows_u, means_u = _cluster_rows(subs_u, _row_gap)
        import os as _osdbg5
        if _osdbg5.environ.get("FIX3_DEBUG"):
            print(f"FIX3DBG row-split {list(bbox)} nrows_u={len(rows_u)} row_sizes={[len(r) for r in rows_u]} row_means={[round(m,1) for m in means_u]} eroded={_eroded}")
        if len(rows_u) < 2:
            return [], len(subs_u)
        # Round 20 track-p21 (b): dark-core subs for the per-row reclaim.
        _core_ink = gray[y0:y1, x0:x1] < 140
        _core_row = _core_ink.sum(axis=1)
        _core_ink = _core_ink.copy()
        _core_ink[_core_row > 0.90 * _core_ink.shape[1], :] = False
        _core_subs_all = _extract_subs(_core_ink, area_floor=20, h_floor=0.25)
        # Round 20 IoU fix: eroded copy for the reclaim EXTENSION only.
        _core_subs_all_ext = _extract_subs(cv2.erode(_core_ink.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool), area_floor=20, h_floor=0.25)
        _cy = lambda s: s[1] + s[3] / 2
        _core_rows = [[] for _ in rows_u]
        for _s in _core_subs_all:
            _j = min(range(len(means_u)), key=lambda j: abs(_cy(_s) - means_u[j]))
            _core_rows[_j].append(_s)
        _core_rows_ext = [[] for _ in rows_u]
        for _s in _core_subs_all_ext:
            _j = min(range(len(means_u)), key=lambda j: abs(_cy(_s) - means_u[j]))
            _core_rows_ext[_j].append(_s)
        # assign each split-sub to the nearest row (by y-centre)
        rows = [[] for _ in rows_u]
        for _s in subs:
            _j = min(range(len(means_u)), key=lambda j: abs(_cy(_s) - means_u[j]))
            rows[_j].append(_s)
        # R19-2a guard (measured): a real text line has >=3 letter pieces. The
        # May title blobs split into fragment rows of [1, 2] subs (their huge
        # letters are filtered by _extract_subs' hh cap, only serifs survive) and
        # three p20 blobs into [1, 1] rows — splitting those replaces a correct
        # whole box with fragment boxes. Reject the whole row-split then (caller
        # keeps the whole word box, exactly as before). Good splits have >=4
        # subs/row (p01 giant box 15-39/row, logo 4-6/row).
        _retried = False
        if any(len(_r) < 3 for _r in rows):
            # ROUND 23 track-misses EXP1 (FOB blob): erosion annihilated the
            # subs (155 uneroded -> 2 eroded in [544,1753,1111,1893]; thin
            # strokes fragment below the area floor). Same R19-2a retry as
            # split_blob_words: retry with the UNERODED subs instead of
            # vetoing the whole split. If the retry also has a <3-sub row,
            # return [] exactly as before.
            if _eroded:
                print(f"row-split retry (uneroded): {list(bbox)} "
                      f"({len(subs)} eroded subs -> {len(subs_u)} uneroded)")
                subs = subs_u
                _eroded = False
                _retried = True
                rows = [[] for _ in rows_u]
                for _s in subs:
                    _j = min(range(len(means_u)), key=lambda j: abs(_cy(_s) - means_u[j]))
                    rows[_j].append(_s)
            if any(len(_r) < 3 for _r in rows):
                return [], len(subs_u)
        words = []
        for _ri, (_row, _row_u) in enumerate(zip(rows, rows_u)):
            if not _row:
                return [], len(subs_u)
            _row_sorted = sorted(_row, key=lambda s: s[0])
            _row_u_sorted = sorted(_row_u, key=lambda s: s[0])
            _ref_w = max(s[0] + s[2] for s in _row_u_sorted) - min(s[0] for s in _row_u_sorted)
            _w, _ok = _split_from_subs(_row_sorted, x0, y0, _row_u_sorted,
                                       mult=1.5 if _eroded else 2.0, ref_w=_ref_w,
                                       core_subs=_core_rows[_ri],
                                       core_subs_ext=_core_rows_ext[_ri])
            if not _ok:
                return [], len(subs_u)
            words.extend(_w)
        if _retried and any((w["box"][3] - w["box"][1]) > 2 * med_h for w in words):
            # ROUND 23 track-misses EXP2 guard: the retry is a second-chance
            # path for PRINT blobs whose erosion annihilated the subs (FOB
            # blob: 155 uneroded -> 2 eroded). A signature scribble retries
            # into a "word" 2.5*med_h tall (p07 [524,2452,785,2517], h=65 at
            # med_h 26) — no single text-line word is that tall (cap height +
            # descender <= ~1.7*med_h). Reject the whole retry then, exactly
            # as before (caller keeps the whole word box). The guard applies
            # ONLY to the retry path; the proven normal path is untouched.
            # Measured: FOB products max h 22 (1.1*med_h), p22 "?" products
            # max h 24 (1.0*med_h) — both pass; p07 signature h 65 fails.
            return [], len(subs_u)
        if len(words) < 2:
            return [], len(subs_u)
        print(f"row-split tall blob {list(bbox)} -> {len(words)} words ({len(rows_u)} rows, {len(subs_u)} pieces)")
        return words, len(subs_u)

    split_boxes, out, split_done = [], [], 0
    split_sources = []  # ROUND 21 FIX C: (orig _comps, part boxes) per split word
    _row_split_failed = set()  # ROUND 21 FIX E: boxes whose row-split returned []
    for wd in words:
        if wd.get("src") in ("blob-split", "rhythm-dp", "core-reclaim"):
            out.append(wd)
            continue
        x0, y0, x1, y1 = wd["box"]
        wpx, hpx = x1 - x0, y1 - y0
        ncomp = max(1, wd.get("n_comp", 1))
        # R19-2a: tall blobs (h > 3*med_h) go to the row-aware split; the
        # handling block below is shared by both paths (fix1-v1 bug: it used to
        # sit inside the first branch only, silently dropping every normal split).
        parts, n_sub = None, 0
        _went_row = False
        if (wpx >= 6 * med_h and hpx <= 3 * med_h):  # 300-DPI FIX F2: no ncomp gate; split_blob_words validates
            parts, n_sub = split_blob_words((x0, y0, x1, y1))
        elif (wpx >= 6 * med_h and hpx > 3 * med_h):
            _went_row = True
            # R19-2a: row-aware split for tall blobs (e.g. p01 giant box
            # [553,1898,975,2037], 5 lines in one span, font_px 139 — the old
            # h <= 3*med_h gate never split it, 48 real line-words F3-dropped).
            parts, n_sub = _row_split_blob((x0, y0, x1, y1))
        if _went_row and not parts:
            # ROUND 21 FIX E: row-split returned [] — this box (e.g. the p13
            # "?" signature graphic) is not a splittable word; remember it so
            # F3 does not let it eat real words overlapping it.
            _row_split_failed.add(tuple(wd["box"]))
        # Round 20 track-p21 v2c: an orphan must not vote to replace a whole
        # word box — it is a fragment, not a word. Measured on p01: "Hi-Tech"
        # (1 real word + 1 orphan "c") and the email "matapltd@matagroup.in"
        # (1 real word + 3 orphans) were replaced by their parts, dropping the
        # "h" and "p.in" (2 NEW T2s on a page that was already REFUSE). The
        # whole box already covers the orphan's letter; replace only when >=2
        # REAL words result.
        _n_real = sum(1 for p in parts if p.get("src") != "core-reclaim") if parts else 0
        if parts is not None and _n_real >= 2:
            print(f"split merged word box {wd['box']} -> {len(parts)} words ({n_sub} pieces)")
            for p in parts:
                out.append({"box": p["box"], "line": wd["line"],
                            "font_px": round(float(p["box"][3] - p["box"][1]), 1),
                            "n_comp": p["n_comp"], "src": p.get("src", "blob-split")})
            split_boxes.append(wd["box"])
            split_sources.append((list(wd.get("_comps", [])), [p["box"] for p in parts]))
            split_done += 1
            continue
        out.append(wd)
    _kept_words, _supp_words = [], []
    for _wd in out:
        if _wd.get("src") in ("blob-split", "rhythm-dp", "core-reclaim", "light-split", "fused-tau") \
                or not any(_inside(_wd["box"], b) for b in split_boxes):
            _kept_words.append(_wd)
        else:
            _supp_words.append(_wd)
    words = _kept_words

    # --- ROUND 21 FIX C (track-misses): comp-coverage reconciliation ---
    # A split replaces a grouped word with dark-sub parts. A letter whose dark
    # ink is fragmented below the area floor (or absent — a grey arc) has NO
    # dark sub, so no part covers it, subcov cannot see it, and the original
    # word is replaced (split) or suppressed (inside a split box). The reclaim
    # orphan guard (w >= 0.5*med_h) then rejects its thin core sub. Measured
    # cases (stage-traced, trace_seg.py): p13 's' of invoices/goods x3 pages
    # (dark max 33 < 34 floor; core sub 9px < 10.5 guard), p08 'i' stem of
    # Uniform (dark max 17; core 4px < 13 guard), p21 't'/'l' [759,1971,767,1999]
    # (core 8px < 14 guard), p21 'i' [784,821,793,834] and 'l' of ability
    # [1025,2221,1033,2249], p01 '0' arc of 2027.69 (NO dark or core sub at
    # all — Otsu-only ink). Root fix: validate the split at the COMP level
    # (Otsu comps, not dark subs). For every comp of a split word and of a
    # suppressed word, if its centre is inside no final word box, extend the
    # nearest same-line word within max(8, 0.5*med_h) px. ROUND 22: the
    # orphan-creation fallback (add a letter-like comp as its own word box)
    # was REMOVED — it never fired on the 33-page corpus (465 extends,
    # 0 orphans, byte-identical outputs with/without it), and by construction
    # it could only fire in the tall-grown-box corner (rev.1: an extension
    # blocked by overlap never falls through to orphan). A comp that cannot
    # extend is left uncovered, never guessed. Extension only ever grows a box
    # toward real ink. No OCR anywhere.
    _comp_reclaims = []
    _gap_c = max(8, 0.5 * med_h)


    def _centre_in_words(_ccx, _ccy):
        for _w in words:
            _b = _w["box"]
            if _b[0] - 2 <= _ccx <= _b[2] + 2 and _b[1] - 2 <= _ccy <= _b[3] + 2:
                return True
        return False


    def _same_band_gap(_cx0, _cy0, _cx1, _cy1, _b):
        _yov = min(_cy1, _b[3]) - max(_cy0, _b[1])
        if _yov < 0.5 * min(_cy1 - _cy0, _b[3] - _b[1]):
            return None
        if _cx0 <= _b[2] and _cx1 >= _b[0]:
            return 0
        return max(_cx0 - _b[2], _b[0] - _cx1)


    _check_comps = []
    for _src_comps, _src_parts in split_sources:
        _check_comps.extend(_src_comps)
    for _wd in _supp_words:
        _check_comps.extend(_wd.get("_comps", []))
    for _c in _check_comps:
        _cx0, _cy0 = _c["x"], _c["y"]
        _cx1, _cy1 = _c["x"] + _c["w"], _c["y"] + _c["h"]
        # ROUND 22 FIX C rev.2 (height floor): only claim letter-sized comps.
        # Measured: every comp FIX C claimed on the PG pages is h<=0.38*med_h
        # (hyphens, dots, specks sitting between words) and claiming them
        # breaks the PG canonical IoU (Aug p1 289->281, May p1 294->285,
        # Aug p6 276->269; suite 35/38). A comp shorter than half the median
        # character height cannot be a letter; FIX C's job is to rescue
        # MISSED WORD PARTS (letter-sized), not to swallow gap marks. The
        # floor costs 1 canonical word on p2 (N5 42->41, desc-L08) and 1 on
        # p3 (249->248) — both still at or above the R21 baseline (40/81,
        # 248/285) — and restores the PG suite to 38/38. No height threshold
        # separates the two cleanly (Raviraj keeps 9px comps, PG has a 10px
        # one), so the principled half-height boundary is used, not a fitted
        # value. See ROUND22-REPORT.md.
        if _cy1 - _cy0 < 0.5 * med_h:
            continue
        _ccx, _ccy = (_cx0 + _cx1) / 2, (_cy0 + _cy1) / 2
        if _centre_in_words(_ccx, _ccy):
            # ROUND 23 track-misses FIX F: a comp whose CENTRE is covered can
            # still stick out on one side — a light-ink letter with no dark sub
            # ('g' of "gal" [687,922,729,956], 'b' of "by" [700,1289,732,1324]:
            # the split cut around the invisible letter, the neighbour box
            # covers only the comp's centre). Measure the overhang instead of
            # trusting the centre: if the comp sticks out beyond its covering
            # word by >= the FIX C gap on ONE side only (the other side <=2px),
            # and the comp is short (<= 2.5*med_h, a fragment not a multi-word
            # fusion), extend the covering word to the full comp bbox — same
            # overlap guard + height cap as the uncovered path below. A comp
            # sticking out on BOTH sides straddles two words (a fusion): skip,
            # do not guess which side owns it.
            _cov_w = None
            for _w in words:
                _b = _w["box"]
                if _b[0] - 2 <= _ccx <= _b[2] + 2 and _b[1] - 2 <= _ccy <= _b[3] + 2:
                    _cov_w = _w
                    break
            if _cov_w is not None:
                _cb = _cov_w["box"]
                _ov_l = _cb[0] - _cx0
                _ov_r = _cx1 - _cb[2]
                if ((_ov_l >= _gap_c and _ov_r <= 2) or (_ov_r >= _gap_c and _ov_l <= 2)) \
                        and (_cx1 - _cx0) <= 2.5 * med_h:
                    _nb = [min(_cb[0], _cx0), min(_cb[1], _cy0),
                           max(_cb[2], _cx1), max(_cb[3], _cy1)]
                    _ov = False
                    for _o in words:
                        if _o is _cov_w:
                            continue
                        _ob = _o["box"]
                        if min(_nb[2], _ob[2]) > max(_nb[0], _ob[0]) \
                                and min(_nb[3], _ob[3]) > max(_nb[1], _ob[1]):
                            _ov = True
                            break
                    if not _ov and _nb[3] - _nb[1] <= 2.5 * med_h and _nb != _cb:
                        _cov_w["box"] = _nb
                        _cov_w["font_px"] = round(float(_nb[3] - _nb[1]), 1)
                        _comp_reclaims.append({"comp": [_cx0, _cy0, _cx1, _cy1],
                                               "mode": "extend-overhang", "box": list(_nb)})
                        print(f"comp-reclaim (overhang): extended box to {_nb} to cover comp "
                              f"{[_cx0, _cy0, _cx1, _cy1]}")
            continue
        _best = None
        for _w in words:
            _g = _same_band_gap(_cx0, _cy0, _cx1, _cy1, _w["box"])
            if _g is not None and _g <= _gap_c and (_best is None or _g < _best[0]):
                _best = (_g, _w)
        if _best is not None:
            _w = _best[1]
            _nb = [min(_w["box"][0], _cx0), min(_w["box"][1], _cy0),
                   max(_w["box"][2], _cx1), max(_w["box"][3], _cy1)]
            # FIX C rev.1: the grown box must not touch any OTHER word. Without
            # this, an extension bridging a word gap turns the grown box into
            # an F3 blocker that eats its neighbour (measured: variant ABCDE
            # changed 70 boxes on p01 for 31 rescued words). If it would
            # overlap a neighbour, leave the comp — do not fall through to the
            # orphan path either.
            _ov = False
            for _o in words:
                if _o is _w:
                    continue
                _ob = _o["box"]
                if min(_nb[2], _ob[2]) > max(_nb[0], _ob[0]) \
                        and min(_nb[3], _ob[3]) > max(_nb[1], _ob[1]):
                    _ov = True
                    break
            if _ov:
                continue
            if _nb[3] - _nb[1] <= 2.5 * med_h and _nb != _w["box"]:
                _w["box"] = _nb
                _w["font_px"] = round(float(_nb[3] - _nb[1]), 1)
                _comp_reclaims.append({"comp": [_cx0, _cy0, _cx1, _cy1],
                                       "mode": "extend", "box": list(_nb)})
                print(f"comp-reclaim: extended box to {_nb} to cover comp "
                      f"{[_cx0, _cy0, _cx1, _cy1]}")
                continue
        # ROUND 22: FIX C orphan path REMOVED (proven dead on the 33-page
        # corpus — 465 extends, 0 orphans in R21; see TRACK-REPORT §orphan).
    print(f"comp-reclaims: {len(_comp_reclaims)}")
    print(f"merged word boxes split: {split_done}")

    print(f"merged word boxes split: {split_done}")
    print(f"merged word boxes split: {split_done}")

    # --- 300-DPI FIX F3: drop words overlapping a larger kept word by >50% ---
    # (highlight-edge / underline fragments overlapping rescued or split title words)
    def _overlap_area(a, b):
        _x0, _y0 = max(a[0], b[0]), max(a[1], b[1])
        _x1, _y1 = min(a[2], b[2]), min(a[3], b[3])
        return max(0, _x1 - _x0) * max(0, _y1 - _y0) if _x1 > _x0 and _y1 > _y0 else 0
    _by_area = sorted(words, key=lambda wd: (wd["box"][2] - wd["box"][0]) * (wd["box"][3] - wd["box"][1]), reverse=True)
    _sat_cache = {}


    def _own_sat(_w):
        """Median HSV saturation of a word's OWN ink (its comps' pixels).
        None if the word has no comp info or <10 ink pixels. Cached by box."""
        _key = tuple(_w["box"])
        if _key in _sat_cache:
            return _sat_cache[_key]
        _res = None
        _sats = []
        for _cc in (_w.get("_comps") or []):
            _lab = _cc.get("lab")
            if _lab is None:
                continue
            _m = (labels[_cc["y"]:_cc["y"] + _cc["h"],
                          _cc["x"]:_cc["x"] + _cc["w"]] == _lab)
            if int(_m.sum()) == 0:
                continue
            _sats.append(_hsv_f3[_cc["y"]:_cc["y"] + _cc["h"],
                                  _cc["x"]:_cc["x"] + _cc["w"], 1][_m])
        if _sats:
            _all = np.concatenate(_sats)
            if len(_all) >= 10:
                _res = float(np.median(_all))
        _sat_cache[_key] = _res
        return _res


    _line_graph = None  # lazy: (adjacency, black-set) for rev.4


    def _build_line_graph(_all_words):
        """Same-line adjacency over all words + the set of BLACK-ink word boxes.
        Edge: y-overlap >= 50% of the smaller height, height ratio in
        [0.7,1.4], x-gap in [0, 2*med_h]. Black: own-ink median sat <= 40."""
        _adj, _black = {}, set()
        _bs = [tuple(w["box"]) for w in _all_words]
        for _w in _all_words:
            _s = _own_sat(_w)
            if _s is not None and _s <= 40:
                _black.add(tuple(_w["box"]))
        for _i, _a in enumerate(_bs):
            for _b in _bs[_i + 1:]:
                _yov = min(_a[3], _b[3]) - max(_a[1], _b[1])
                if _yov < 0.5 * min(_a[3] - _a[1], _b[3] - _b[1]):
                    continue
                _hr = (_b[3] - _b[1]) / max(1, _a[3] - _a[1])
                if not (0.7 <= _hr <= 1.4):
                    continue
                _gap = max(_a[0] - _b[2], _b[0] - _a[2])
                if _gap < 0 or _gap > 2 * med_h:
                    continue
                _adj.setdefault(_a, set()).add(_b)
                _adj.setdefault(_b, set()).add(_a)
        return _adj, _black


    def _reaches_black(_box, _adj, _black):
        """BFS from _box over the line graph; True iff a black word is reached."""
        _seen = {tuple(_box)}
        _front = [tuple(_box)]
        while _front:
            _cur = _front.pop()
            if _cur in _black:
                return True
            for _n in _adj.get(_cur, ()):  # neighbours of a black word included
                if _n not in _seen:
                    _seen.add(_n)
                    _front.append(_n)
        return False

    _kept, _dropped_overlap = [], 0
    _hsv_f3 = None  # lazy: only needed when a resurrected word is checked
    _SPLIT_SRCS = ("blob-split", "rhythm-dp", "core-reclaim", "light-split", "fused-tau")  # R26 TAU: tau products are split products for F3
    for _wd in _by_area:
        _area = (_wd["box"][2] - _wd["box"][0]) * (_wd["box"][3] - _wd["box"][1])
        _blockers = [_k for _k in _kept
                     if tuple(_k["box"]) not in _row_split_failed
                     and _overlap_area(_wd["box"], _k["box"]) > 0.5 * _area]
        if _wd.get("src") != "comp-reclaim" and _blockers:
            # ROUND 23 track-misses EXP2 (FOB digits): a VALIDATED split
            # product ([754,1874,818,1892] "56775", [826,1874,851,1892] "21",
            # [780,1899,804,1915] FREIGHT "69") was F3-dropped by the fused
            # multi-row blob [779,1873,856,1918] (77x45, 1 comp, spans the FOB
            # AND FREIGHT rows) that merely overlaps it. A kept word taller
            # than 2*med_h spans two text rows — it is fused, not a word — and
            # must yield to a validated split product: remove the fused
            # keeper(s) and keep the split word. All blockers must be fused
            # multi-row NORMAL words; if any blocker is a genuine single-row
            # word, drop the fragment exactly as before.
            _fused = [ _k for _k in _blockers
                       if _k.get("src") not in _SPLIT_SRCS
                       and (_k["box"][3] - _k["box"][1]) > 2 * med_h ]
            if _wd.get("src") in _SPLIT_SRCS and len(_fused) == len(_blockers):
                for _k in _fused:
                    _kept.remove(_k)
                    print(f"F3 swap: removed fused keeper {_k['box']} for split word {_wd['box']}")
                _dropped_overlap += len(_fused)
            else:
                print(f"dropped overlapping fragment {_wd['box']}")
                _dropped_overlap += 1
                continue
        # FIX E rev.1/rev.4: a word that survives ONLY because its blocker
        # failed its row-split is "resurrected" — FIX E also resurrects seal/
        # stamp lettering (measured: p13 blue-seal fragments "1949"/"AHMEDABAD"
        # and orange-graphic bits, own-ink median saturation 125-218) alongside
        # real print (p01 invoice block, 0; p13 digits "202", 0). Colour alone
        # does NOT separate them: p13's digit "6" is itself coloured ink
        # (own-ink median sat 153, frac>80 0.64 — a dark saturated digit on the
        # same baseline as the black "202"), and p01's FOB/FREIGHT digits are
        # saturated too (med sat 83-97 — printed over/merged with the red
        # stamp). The separator is LINE MEMBERSHIP (rev.4): a saturated
        # resurrected word is kept iff it is connected, through a chain of
        # same-line words (y-overlap >= 50%, height ratio in [0.7,1.4], x-gap
        # <= 2*med_h), to a BLACK-ink word. The "6" reaches black "2"; the p01
        # digits reach black "USD"/"FOB" through the number; seal fragments
        # chain only to other saturated fragments. Words without comp info are
        # kept (no evidence).
        if _wd.get("src") != "comp-reclaim" and any(
                _overlap_area(_wd["box"], _k["box"]) > 0.5 * _area for _k in _kept
                if tuple(_k["box"]) in _row_split_failed):
            if _hsv_f3 is None:
                _hsv_f3 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            _own = _own_sat(_wd)
            if _own is not None and _own > 40:
                if _line_graph is None:
                    _line_graph = _build_line_graph(words)
                if not _reaches_black(_wd["box"], _line_graph[0], _line_graph[1]):
                    print(f"dropped resurrected stamp word {_wd['box']} "
                          f"(own-ink median sat {_own:.0f}, not on a black line)")
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
        # ROUND 26 TRACK-TAU: "fused-tau" skips dash re-splitting, like the
        # other split-product srcs.
        if wd.get("src") in ("blob-split", "rhythm-dp", "core-reclaim", "fused-tau"):
            _dashed.append(wd)
            continue
        _parts = _dash_split(wd)
        if len(_parts) > 1:
            _ndash += 1
        _dashed.extend(_parts)
    words = _dashed
    print(f"dash splits: {_ndash}")

    # --- ROUND 21 FIX D (track-misses): frag gap-attach, integrated ---
    # Round 20 track-frag proved this post-hoc Otsu gap-attach standalone
    # (gate 17/8 -> 20/5) and the R20 merge measured it subsumed on top of
    # reclaim2c on the 25 Raviraj pages (0 rescues) but still live on canonical
    # p2 (2 rescues: "CY" of AGENCY, "BH" of BHULTA — score-neutral, real ink
    # coverage). The R20 report left integration as open work (ROUND20 §14.6).
    # It is integrated here, in the segmenter itself (not a post-hoc script),
    # at exactly the track-frag position (after F3 + dash-split). Extension
    # only: no box is created or deleted, no word merges into another, word
    # COUNT never changes. A word-like uncovered cluster (gate T2 thresholds)
    # extends its same-line neighbour within max(8, 0.5*med_h) px; both sides
    # -> left (reading order). Single-CC fragments are NOT rescued here (the
    # T2 test needs n_cc>=2) — those are FIX C's comp-reconciliation. No OCR.
    _frag_rescues = []
    try:
        from .gate_misses import uncovered_clusters as _frag_clusters, \
            detect_seal_regions as _frag_seals
        _frag_seal_boxes = _frag_seals(img, gray)
        _frag_raw = _frag_clusters(gray, words, med_h)
        _frag_gap = max(8, 0.5 * med_h)
        for _c in _frag_raw:
            _cx0, _cy0, _cx1, _cy1 = _c["box"]
            _ch, _cw = _cy1 - _cy0, _cx1 - _cx0
            if _cy0 >= sig_y:
                continue  # signature zone: mask never touches it
            if LOGO is not None and _cx0 >= LOGO[0] and _cy0 >= LOGO[1] \
                    and _cx1 <= LOGO[2] and _cy1 <= LOGO[3]:
                continue  # detected logo rect
            if _ch >= 150 and _cw <= 10:
                continue  # vertical rule
            if _cw >= 150 and _ch <= 10:
                continue  # horizontal rule
            if not (_c["n_cc"] >= 2 and _ch >= 12 and _cw >= 20 and _c["area"] >= 150
                    and _c["med_cc_h"] >= 10 and _c["med_cc_area"] >= 25):
                continue  # fragment / halftone dots / speck (gate T2 word-like test)
            _ov = 0
            for _wd in words:
                _b = _wd["box"]
                _ox = max(0, min(_cx1, _b[2]) - max(_cx0, _b[0]))
                _oy = max(0, min(_cy1, _b[3]) - max(_cy0, _b[1]))
                _ov = max(_ov, _ox * _oy)
            if _ov >= 0.5 * _cw * _ch:
                continue
            _ccx, _ccy = (_cx0 + _cx1) / 2, (_cy0 + _cy1) / 2
            if any(_b[0] <= _ccx <= _b[2] and _b[1] <= _ccy <= _b[3]
                   for _b in _frag_seal_boxes):
                continue  # seal lettering, not a real word
            _left = _right = None
            for _wd in words:
                _b = _wd["box"]
                _yov = min(_cy1, _b[3]) - max(_cy0, _b[1])
                if _yov < 0.5 * min(_ch, _b[3] - _b[1]):
                    continue  # not the same line
                _wh = _b[3] - _b[1]
                if not (0.4 * _wh <= _ch <= 1.8 * _wh):
                    continue  # height mismatch: not the same text line
                _gl = _cx0 - _b[2]
                _gr = _b[0] - _cx1
                if 0 <= _gl <= _frag_gap and (_left is None or _gl < _left[0]):
                    _left = (_gl, _wd)
                if 0 <= _gr <= _frag_gap and (_right is None or _gr < _right[0]):
                    _right = (_gr, _wd)
            _target = _side = None
            if _left is not None:
                _target, _side = _left[1], "left"
            elif _right is not None:
                _target, _side = _right[1], "right"
            if _target is None:
                continue  # no same-line neighbour in the gap: leave for the gate
            _old = list(_target["box"])
            _target["box"] = [min(_old[0], _cx0), min(_old[1], _cy0),
                              max(_old[2], _cx1), max(_old[3], _cy1)]
            _target["font_px"] = round(float(_target["box"][3] - _target["box"][1]), 1)
            _frag_rescues.append({"cluster": _c["box"], "n_cc": _c["n_cc"],
                                  "area": _c["area"], "side": _side,
                                  "old_box": _old, "new_box": list(_target["box"]),
                                  "line": _target.get("line")})
            print(f"frag-rescue cluster {_c['box']} (n_cc={_c['n_cc']}) -> "
                  f"extend {_side} word {_old} to {_target['box']}")
    except Exception as _e:
        print(f"frag-rescue skipped (error {_e})")
    print(f"frag-rescues: {len(_frag_rescues)}")

    # strip internal component lists (output format identical to v3)
    for _wd in words:
        _wd.pop("_comps", None)

    # --- ROUND 21 TRACK-P12 (v5): release of black print fused into a giant
    # ink network by a blue signature stroke ("P" of Prepared, Raviraj p12).
    # This REPLACES the Round 20 track-gateside v4 comp-injection
    # (segment_gateside.py), which fixed p12 but broke p10 (a 1px box touch
    # mis-assigns a signature core to the widened "By") and split p09's
    # "Prepared" 1->3, and left a 0.455 near-miss on p12 "Approved" — all three
    # side effects came from injected comps shifting LINE GROUPING, not from
    # the release itself (measured: the freed pieces are the same either way).
    # v5 therefore NEVER injects a comp and NEVER re-runs grouping/splitting:
    # the pipeline runs exactly as the R20 merged baseline, and only AFTER the
    # final word list exists are freed pieces resolved against it:
    #   (a) a NARROW piece (w <= 1.75*med_h — a single letter/fragment) EXTENDS
    #       the box of the single neighbouring word it unambiguously belongs
    #       to; word count never changes for these;
    #   (b) a WIDE piece (w > 1.75*med_h) becomes its OWN word box. The bound
    #       is measured, not tuned: on these pages the page's own letter-comp
    #       widths are p99 = 1.58*med_h (41px at med_h 26); no single glyph
    #       reaches 1.75*med_h, so a 57px black piece ("By", p11, eye-verified)
    #       is >=2 letters, i.e. a word in its own right — attaching it to the
    #       neighbour would MERGE two words (measured wrong on p11 v5-draft:
    #       "Prepared By" became one box [660,893]). A wide piece with no
    #       neighbour on the same line is SKIPPED, never invented standalone.
    # Freed-piece tests are v4's own, unchanged (giant CC w>900 or h>180,
    # rule-shaped giants skipped; de-blue B-R>50 inside the giant mask only;
    # letter-sized 0.4*med_h<=h<=2.5*med_h, w<=2.5*med_h, area>=14; black
    # print-like median B-R<=15; outside the logo exclusion). Two extra guards:
    #   - piece centre must be ABOVE sig_y (the pipeline's own signature
    #     cutoff; nothing below it becomes a word — this keeps the 21 freed
    #     CARRIER-NAME pieces on p01 and the 2 on canonical p2, all below
    #     their sig_y, out of the seg entirely);
    #   - a piece bridging two words is skipped, never guessed (reclaim rule 2).
    # A freed piece already >=50% covered by an existing word box is skipped.
    _released = []
    _new_words = []
    for _gi in range(1, num):
        _gx, _gy, _gw, _gh, _ga = (int(v) for v in stats[_gi])
        if not (_gw > 900 or _gh > 180):
            continue
        if (_gw > 375 and _gh <= 15) or (_gh > 150 and _gw <= 15):
            continue  # rule-shaped giant: not a fusion network
        _gmask = (labels[_gy:_gy + _gh, _gx:_gx + _gw] == _gi).astype(np.uint8)
        _bgr = img[_gy:_gy + _gh, _gx:_gx + _gw]
        _is_blue = ((_bgr[:, :, 0].astype(np.int16) - _bgr[:, :, 2].astype(np.int16)) > 50) & (_gmask > 0)
        if not _is_blue.any():
            continue
        _gmask[_is_blue] = 0
        _n2, _lab2, _st2, _cen2 = cv2.connectedComponentsWithStats(_gmask, connectivity=8)
        _pieces = []
        for _j in range(1, _n2):
            _px, _py, _pw, _ph, _pa = (int(v) for v in _st2[_j])
            if _pw > 900 or _ph > 180:
                continue  # still-giant remainder, not a freed piece
            if _pa < 14 or _ph < 0.4 * med_h or _ph > 2.5 * med_h or _pw > 2.5 * med_h:
                continue  # not letter-sized (rule sliver / frame / speck)
            _ax, _ay = _gx + _px, _gy + _py
            _pm = (_lab2[_py:_py + _ph, _px:_px + _pw] == _j)
            _ppx = img[_ay:_ay + _ph, _ax:_ax + _pw][_pm]
            _med_br = float(np.median(_ppx[:, 0].astype(np.int16) - _ppx[:, 2].astype(np.int16))) if len(_ppx) else 0.0
            if _med_br > 15:
                continue  # coloured ink (signature fragment / blue print), not black print
            if in_excluded(_ax, _ay, _pw, _ph):
                continue
            _pieces.append((_ay, _ax, _ax, _ay, _ax + _pw, _ay + _ph, _med_br))
        _pieces.sort()  # raster order, so a wide piece resolves before its tail
        for (_sy, _sx, _ax, _ay, _ax1, _ay1, _med_br) in _pieces:
            _pb = [_ax, _ay, _ax1, _ay1]
            _pw, _ph = _ax1 - _ax, _ay1 - _ay
            _pcy = _ay + _ph / 2.0
            if _pcy >= sig_y:
                continue  # below the signature cutoff: never a word
            # already covered by an existing word box? nothing to do.
            _cov = False
            for _wd in words:
                _b = _wd["box"]
                _ox = max(0, min(_pb[2], _b[2]) - max(_pb[0], _b[0]))
                _oy = max(0, min(_pb[3], _b[3]) - max(_pb[1], _b[1]))
                if _ox * _oy >= 0.5 * _pw * _ph:
                    _cov = True
                    break
            if _cov:
                continue
            _cands = []
            for _wi, _wd in enumerate(words):
                _b = _wd["box"]
                if not (_b[1] - 0.5 * med_h <= _pcy <= _b[3] + 0.5 * med_h):
                    continue  # not the same line band
                if _pb[2] < _b[0]:
                    _gap = _b[0] - _pb[2]
                elif _pb[0] > _b[2]:
                    _gap = _pb[0] - _b[2]
                else:
                    _gap = 0  # x-overlap: piece hangs off the word's side
                if _gap <= 1.0 * med_h:
                    _cands.append((_gap, _wi))
            if not _cands:
                continue  # no clear neighbour: skip, do not invent a word
            _cands.sort()
            if len(_cands) > 1 and _cands[1][0] < _cands[0][0] + 0.5 * med_h:
                continue  # ambiguous: bridges two words, never guess a side
            _wi = _cands[0][1]
            if _pw > 1.75 * med_h:
                # >=2 letters: its own word on the neighbour's line.
                _nw = {"box": list(_pb), "line": words[_wi].get("line"),
                       "font_px": round(float(_ph), 1), "n_comp": 1,
                       "src": "giant-release"}
                words.append(_nw)
                _new_words.append(_nw)
                _released.append({"piece": _pb, "new_word": True,
                                  "line": words[_wi].get("line"),
                                  "med_b_r": round(_med_br, 1)})
            else:
                _b = words[_wi]["box"]
                words[_wi]["box"] = [min(_b[0], _pb[0]), min(_b[1], _pb[1]),
                                    max(_b[2], _pb[2]), max(_b[3], _pb[3])]
                words[_wi]["n_comp"] = words[_wi].get("n_comp", 1) + 1
                _released.append({"piece": _pb, "word_idx": _wi,
                                  "old_box": _b, "new_box": list(words[_wi]["box"]),
                                  "med_b_r": round(_med_br, 1)})
    if _new_words:
        words = sorted(words, key=lambda wd: (wd.get("line", 0), wd["box"][0]))
    if _released:
        print(f"p12v5 release: resolved {len(_released)} freed print piece(s): {_released}")

    print(f"words segmented: {len(words)}")
    return {"image": image_name, "method": "connected-components, no recognition (v5-300: v4-300 + R6 cluster-anchor signature zone; R19 merge: logo rect per-page + sigy anchor check + top2a all-cuts/subcov/row-split + top2b rhythm-DP fallback)",
            "median_char_h_px": med_h, "sig_y_detected": sig_y,
            "r20_p21_hybrid": "dark-core reclaim v2c ONLY, no gap floor (CORE_THR 140, core area_floor 20 + h_floor 0.25, 2D orphan clustering, V3 orphan-vote fix)",
            "r22_p20_light_print": "light-print fallback in split_blob_words: Otsu-sub split (cut >= max(5, 0.30*med_h), uniform-spacing guard min_pos <= 0.5*max_pos) when dark subs are empty; src light-split",
            "logo_rect_detected": list(LOGO) if LOGO is not None else None,
            "rescued_blobs": rescued,
            "footer_words": [w["box"] for w in words if w["box"][1] >= sig_y],
            "comp_reclaims": _comp_reclaims,
            "frag_rescues": _frag_rescues,
            "words": words}


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
