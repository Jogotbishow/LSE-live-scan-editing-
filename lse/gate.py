"""Round 20 merged seg-completeness gate for full-page CC-mask.

Evolved from Round 17 Track B (gate_ccmask.py): the fixed logo rect
(150,120,510,450) is GONE — the exclusion rect is detected per page
(logo_detect.detect_logo_rect); blue seal regions are excluded
(detect_seal_regions); sig_y uses the anchor check. The -2 band rule
(DECISIONS.md, cw > 120) is kept in full_page_mask() — same surgical
block as ccmask.full_page_clean(). Round 20 adds the G2 gateside rule
(line-band core-assignment fix: a T1 flag is suppressed iff more than
half of the core's pixels lie outside its word's LINE band). See
improve/ROUND20-REPORT.md (Raviraj gate 17/8 -> 23/2).

Original Round 17 purpose:

Purpose: make build-time CC-mask safe. The gate must guarantee NO silently-
erased seg-missed word: it REFUSEs (never erases) when it finds word-like
ink the seg does not cover, and only ALLOWs when the page is complete.

Two independent tests (either one REFUSEs):
  T1 core-outside: every core CC assigned to a word must lie (nearly)
     inside that word's box. A core that sticks far outside its assigned
     box is ink belonging to another (missed) word — exactly how the R16
     "68.02" case was erased (cores overlapped a neighbour's box by a few
     rows). Flag: outside_frac > 0.25 AND extension > 6 px beyond the box.
     Threshold calibrated from data (see calibrate()): on correctly
     oriented pages the max outside_frac is ~0.00-0.02.
  T2 word-like uncovered cluster: R16 miss-hunt clustering verbatim
     (Otsu CCs, centre in no word box +2px, row-chain, x-gap split),
     then word-like (n_cc>=2, h>=12, w>=20, area>=150, median CC
     height>=10, median CC area>=25, overlap with any word box <50%)
     AND outside the exclusions below. Exclusions (mirroring what the
     mask itself never touches): logo rect (150,120,510,450) — the mask
     zeroes it, so ink there can never be erased; signature zone
     (y0 >= sig_y, inpaint v4 rule); rule-shaped clusters; halftone dots
     (median CC height < 10).

Also in this module: full_page_mask(img, seg, rule_exclusion) — a faithful
mirror of R16 inpaint_ccmask2.full_page_clean's mask construction, with the
rule exclusion switchable, so mask px before/after exclusion can be measured
on correctly oriented pages. The mirror is validated by reproducing R16's
Aug-p2 JPG numbers exactly (397,661 / 69,058) before any PNG is measured.

Background (measured R17, not assumed): R16 Track C ran fullpage on
aug-p2-orig.jpg, which is the Aug p2 page ROTATED 180 deg relative to the
live-page PNG (mean abs diff vs PNG: 17.06 rotated vs 27.96 as-is; the
"68.02" at JPG x310-390 is the 180-deg rotation of the true value at PNG
x2097-2187, y1394-1422 — which HAS a seg box [2097,1394,2187,1422]).
So the R16 "seg-missed 68.02 / silent data loss" case is an artefact of a
rotated source image, not a property of the true page. This gate is
validated on correctly oriented pages (PNGs), on the rotated JPG (must
REFUSE), and on synthetic misses (a deleted seg box must REFUSE).

No OCR anywhere. Reads images/segs read-only; writes only this track dir.
Usage (from scan-paper/):
  venv/bin/python improve/round17/track-b/gate_ccmask.py gate IMG SEG
  venv/bin/python improve/round17/track-b/gate_ccmask.py mask IMG SEG
  venv/bin/python improve/round17/track-b/gate_ccmask.py calibrate IMG SEG
"""
import json
import sys

import cv2
import numpy as np

from .ccmask import INK_THR, assign_cores, core_ccs, detect_sig_y
from .logo_detect import detect_logo_rect
# ROUND 19 TRACK-LOGO: the fixed LOGO rect (150,120,510,450) is GONE here
# too — it hid real seg misses (DIAGNOSIS.md §4.3: Goods, GO, ORIGINAL...).
# The T2 logo exclusion and the mask zeroing now use the SAME per-page
# detected rect as segment_logo.py (logo_detect.detect_logo_rect), so the
# gate can no longer hide a miss the segmenter made. None = no exclusion.

def detect_seal_regions(img, gray):
    """Round 19 Track-sigy — blue round-seal regions (stamp exclusion).

    Colour separation (S26 seal-extractor principle, re-measured for BLUE
    seals: that repo is tuned for Chinese RED seals; ours are blue, so the
    channel test is B-R > 50 per CC) + shape as second vote (S31 ellipse
    idea, bbox form): blue CCs chained with a 60px gap; a cluster is a
    seal region iff w,h in [120,600], 0.5 <= w/h <= 2.0, n_cc >= 8,
    area >= 2000. Measured on 32 pages: detects the GCC stamp (p13) and
    the RAVIRAJ seal (p16/p17/p18/p19) and nothing else; the 3 stamp
    flags fall inside, 0 real flags do (wide light-blue letterhead text
    fails the w/h shape test; the GCCI blue text logo fails h >= 120;
    the MATA blue logo fails n_cc >= 8). HoughCircles was tried first
    and REJECTED (0 circles on p13/p16, false positives elsewhere);
    large hollow-CC rings were tried and REJECTED (table frames).
    Returns a list of [x0, y0, x1, y1] seal boxes. No OCR, no model."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num, labels, stats, _cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    blue = []
    for i in range(1, num):
        x, y, ww, hh, area = (int(v) for v in stats[i])
        if area < 8 or ww > 900 or hh > 180:
            continue
        m = (labels[y:y + hh, x:x + ww] == i)
        px = img[y:y + hh, x:x + ww][m]
        if len(px) == 0:
            continue
        mb, _mg, mr = px.mean(axis=0)
        if mb - mr > 50:
            blue.append({"box": [x, y, x + ww, y + hh], "area": area})
    clusters = []
    for b in sorted(blue, key=lambda c: (c["box"][1], c["box"][0])):
        placed = False
        for cl in clusters:
            x0 = min(c["box"][0] for c in cl)
            y0 = min(c["box"][1] for c in cl)
            x1 = max(c["box"][2] for c in cl)
            y1 = max(c["box"][3] for c in cl)
            if (b["box"][0] - x1 <= 60 and x0 - b["box"][2] <= 60
                    and b["box"][1] - y1 <= 60 and y0 - b["box"][3] <= 60):
                cl.append(b)
                placed = True
                break
        if not placed:
            clusters.append([b])
    seals = []
    for cl in clusters:
        x0 = min(c["box"][0] for c in cl)
        y0 = min(c["box"][1] for c in cl)
        x1 = max(c["box"][2] for c in cl)
        y1 = max(c["box"][3] for c in cl)
        w, h = x1 - x0, y1 - y0
        area = sum(c["area"] for c in cl)
        if (120 <= w <= 600 and 120 <= h <= 600 and 0.5 <= w / h <= 2.0
                and len(cl) >= 8 and area >= 2000):
            seals.append([x0, y0, x1, y1])
    return seals


def _in_seal(boxes, cx, cy):
    for b in boxes:
        if b[0] <= cx <= b[2] and b[1] <= cy <= b[3]:
            return True
    return False

def detect_sig_y_gate(gray, h):
    """Gate's own signature-row detector: same rule as inpaint.py v4
    (tall handwriting strokes in bottom 30%) but 1.8x median letter
    height instead of 2.2x. Measured R17: v4's 2.2x finds only ONE tall
    CC on aug-p5 (needs >=2), so sig_y silently falls back to h=3467
    and the handwriting below is unprotected; at 1.8x there are 8 tall
    CCs, min y=2856, which excludes exactly the signature block. The
    shared inpaint.py v4 is NOT changed; this is gate-local."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num, _labels, stats, _cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    letter_h, tall = [], []
    for i in range(1, num):
        x, y, ww, hh, area = stats[i]
        if area < 14:
            continue
        if (ww > 375 and hh < 9) or (hh > 180 and ww < 9):
            continue
        if ww > 900 or hh > 180:
            continue
        letter_h.append(hh)
        tall.append((x, y, ww, hh))
    med_h = sorted(letter_h)[len(letter_h) // 2] if letter_h else 18
    tall = [t for t in tall if t[1] > 0.7 * h and t[3] > 1.8 * med_h and t[2] < 300]
    return min(t[1] for t in tall) if len(tall) >= 2 else h
# R17 calibration: on correctly oriented pages, 3/1543 cores have
# outside_frac > 0.05 (max 0.308: a 307px halftone-band core and a 14px
# edge fragment) — so 0.25 would false-REFUSE. 0.50 + word-size guard
# (cw<=120, ch<=80) clears all correct pages (measured); the rotated-JPG
# "68.02" digits sit at frac ~0.82, and the rotated JPG has 188 cores
# above 0.25, so 0.50 keeps a wide margin on both sides.
CORE_OUT_FRAC = 0.50   # fraction of a core's pixels outside its word box
CORE_OUT_EXT = 6       # px the core must extend beyond the box edge

# --- ROUND 21 TRACK-P12: minimum-assignment floor for T1 cores ---
# assign_cores assigns a core to a word on ANY nonzero pixel overlap —
# even a single pixel where a box edge grazes a neighbouring stroke.
# After the v5 release widens p10's "By" box to its true y-tail
# ([691,2495,758,2535]), the blue signature core [757,2487,785,2509]
# touches it by exactly 1 ink pixel and is blamed on "By" (T1 0.932) —
# a false flag for ink that is not that word's letter. The gate judges
# cores by their PIXELS, so an assignment must also be pixel-meaningful:
# a core is only judged against a word if it shares at least
# MIN_CORE_ASSIGN_PX ink pixels with that word's (unpadded) box.
# Value from the 33-page population (see TRACK-REPORT.md §5): among
# T1-judgeable cores (area>=100, letter shape) on all 33 baseline pages,
# the smallest genuine letter-core overlap is 8px (p12's real "P" core);
# NO assigned core in the baseline population has best in 1..7 at all.
# In the v5 world exactly one new assignment appears, the p10 stroke
# core with best=1px. So the floor 4 sits in the measured empty interval
# [2,7] between the grazing 1px assignment and the smallest genuine 8px
# overlap, and changes exactly ONE assignment on 33 pages. T1's own
# thresholds (0.50 / 6px) are NOT touched, and no test expectation is
# changed. Applied in gate() and calibrate() only; full_page_mask()
# (inpaint path) is left on the original assignment.
MIN_CORE_ASSIGN_PX = 4


def _assign_cores_min(lab, stats, words):
    """assign_cores with a minimum pixel-overlap floor: assignments
    resting on fewer than MIN_CORE_ASSIGN_PX shared ink pixels are
    demoted to unassigned (-1). Ambiguous (-2) assignments are untouched.
    Returns (assign, ambiguous) in assign_cores' format."""
    assign, ambiguous = assign_cores(lab, stats, words)
    for i, wi in list(assign.items()):
        if wi < 0:
            continue
        x, y, cw, ch, area = (int(v) for v in stats[i])
        m = (lab[y:y + ch, x:x + cw] == i)
        best = 0
        for wd in words:
            bx0, by0, bx1, by1 = wd["box"]
            ox0, oy0 = max(x, bx0), max(y, by0)
            ox1, oy1 = min(x + cw, bx1), min(y + ch, by1)
            if ox1 <= ox0 or oy1 <= oy0:
                continue
            best = max(best, int(m[oy0 - y:oy1 - y, ox0 - x:ox1 - x].sum()))
        if best < MIN_CORE_ASSIGN_PX:
            assign[i] = -1
    return assign, ambiguous

# -2 band rule (DECISIONS.md): band-shaped ambiguous core, not a word.
BAND_CORE_MIN_W = 120


def is_rule_shaped(cw, ch, area):
    fill = area / max(1, cw * ch)
    return ((cw >= 150 and ch <= 10) or (ch >= 150 and cw <= 10)
            or (max(cw, ch) >= 150 and fill < 0.20))


def full_page_mask(img, seg, rule_exclusion=True):
    """Mirror of R16 full_page_clean mask construction (mask only, no
    inpaint). Returns (mask_uint8, info)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    words = seg["words"]
    sig_y = detect_sig_y(gray, h)
    lab, stats = core_ccs(gray)
    assign, ambiguous = assign_cores(lab, stats, words)
    ink = (gray < INK_THR)
    cores = np.zeros((h, w), dtype=np.uint8)
    n_rule_excluded = 0
    for i, wi in assign.items():
        if wi == -1:
            continue
        x, y, cw, ch, area = stats[i]
        # -2 BAND RULE, SURGICAL (DECISIONS.md): band-shaped ambiguous
        # (-2) core (cw > 120) is a highlight/rule, not a word — never
        # in the mask. BUT the core is often FUSED with word ink (May:
        # the dotted title band is one CC with the title letters), so
        # the exclusion is surgical: keep the part INSIDE word boxes
        # (those pixels are letters), drop the part outside (the
        # highlight dots). Whole-core exclusion would un-erase the
        # title words. (Same block in ccmask.full_page_clean.)
        if wi == -2 and cw > BAND_CORE_MIN_W:
            n_rule_excluded += 1
            m = (lab[y:y + ch, x:x + cw] == i).astype(np.uint8)
            keep = np.zeros((ch, cw), dtype=np.uint8)
            for wd in words:
                x0, y0, x1, y1 = wd["box"]
                ix0, iy0 = max(x0, x), max(y0, y)
                ix1, iy1 = min(x1, x + cw), min(y1, y + ch)
                if ix1 > ix0 and iy1 > iy0:
                    keep[iy0 - y:iy1 - y, ix0 - x:ix1 - x] = 1
            m = (m & keep).astype(np.uint8) * 255
            cores[y:y + ch, x:x + cw] = np.maximum(
                cores[y:y + ch, x:x + cw], m)
            continue
        if rule_exclusion and is_rule_shaped(cw, ch, area):
            n_rule_excluded += 1
            continue
        m = (lab[y:y + ch, x:x + cw] == i).astype(np.uint8) * 255
        cores[y:y + ch, x:x + cw] = np.maximum(cores[y:y + ch, x:x + cw], m)
    ker = np.ones((3, 3), np.uint8)
    mask = (cv2.dilate(cores, ker, iterations=1) > 0) & ink
    mask = mask.astype(np.uint8) * 255
    logo_rect, _li = detect_logo_rect(gray)
    if logo_rect is not None:
        mask[logo_rect[1]:logo_rect[3], logo_rect[0]:logo_rect[2]] = 0
    mask[sig_y:h, :] = 0
    return mask, {"mask_px": int((mask > 0).sum()), "sig_y": int(sig_y),
                  "logo_rect": list(logo_rect) if logo_rect is not None else None,
                  "ambiguous_cores": len(ambiguous),
                  "rule_cores_excluded": n_rule_excluded}


def uncovered_clusters(gray, words, med_h):
    """R16 miss-hunt clustering verbatim (dbnet_crosscheck.py). Returns
    raw clusters (before word-like/exclusion filters)."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    ccs = []
    for i in range(1, n):
        cx, cy, cw, ch, area = (int(v) for v in stats[i])
        if area < 4:
            continue
        if cw > 2.5 * med_h or ch > 2.0 * med_h:
            continue
        ccs.append({"box": [cx, cy, cx + cw, cy + ch], "area": area})
    word_boxes = [[w["box"][0] - 2, w["box"][1] - 2, w["box"][2] + 2, w["box"][3] + 2]
                  for w in words]

    def covered(cc):
        cx = (cc["box"][0] + cc["box"][2]) / 2
        cy = (cc["box"][1] + cc["box"][3]) / 2
        for b in word_boxes:
            if b[0] <= cx <= b[2] and b[1] <= cy <= b[3]:
                return True
        return False

    unc = [c for c in ccs if not covered(c)]
    unc.sort(key=lambda c: (c["box"][1] + c["box"][3]) / 2)
    rows = []
    for c in unc:
        placed = False
        for row in rows:
            y0 = min(x["box"][1] for x in row)
            y1 = max(x["box"][3] for x in row)
            ov = min(c["box"][3], y1) - max(c["box"][1], y0)
            if ov > 0.4 * min(c["box"][3] - c["box"][1], y1 - y0):
                row.append(c)
                placed = True
                break
        if not placed:
            rows.append([c])
    clusters = []
    for row in rows:
        row = sorted(row, key=lambda c: c["box"][0])
        heights = [c["box"][3] - c["box"][1] for c in row]
        cap = float(np.median(heights)) if heights else med_h
        cap = max(cap, 8.0)
        cur = [row[0]]
        groups = []
        for c in row[1:]:
            gap = c["box"][0] - cur[-1]["box"][2]
            if gap > 0.30 * cap:
                groups.append(cur)
                cur = [c]
            else:
                cur.append(c)
        groups.append(cur)
        for g in groups:
            x0 = min(c["box"][0] for c in g)
            x1 = max(c["box"][2] for c in g)
            y0 = min(c["box"][1] for c in g)
            y1 = max(c["box"][3] for c in g)
            area = sum(c["area"] for c in g)
            hh, ww = y1 - y0, x1 - x0
            if hh < 8 or ww < 6 or area < 20:
                continue
            if hh < 0.35 * cap:
                continue
            cc_heights = sorted(c["box"][3] - c["box"][1] for c in g)
            cc_areas = sorted(c["area"] for c in g)
            clusters.append({
                "box": [x0, y0, x1, y1], "n_cc": len(g), "area": area,
                "cap": round(cap, 1),
                "med_cc_h": float(cc_heights[len(cc_heights) // 2]),
                "med_cc_area": float(cc_areas[len(cc_areas) // 2]),
                "ccs": [c["box"] for c in g],
            })
    return clusters


# ---- ROUND 21 TRACK-GATE: T3 whole-line collapse check ----
# Lesson (R20 §11.b): the gate was BLIND to whole-line collapse. When
# rhythm_dp.py was missing from the merge dir, the segmenter's DP import
# failed silently, top2a-failed blobs survived as ONE box for a whole
# line (nodp p21 L2379: 19 words in [555,2379,2028,2419]), and the gate
# still said ALLOW (23/2) -- no uncovered cluster, no T1. Only the p21
# GT scorer caught it (35/42 -> 17/42).
#
# What was MEASURED first (and REJECTED -- see TRACK-REPORT.md):
#   * 30x med_h width guard: R19 valid max was 27.0x, collapsed 52.6x.
#     On the R20 baseline it FALSE-POSITIVES: p20 has a genuine 57.4x
#     box, p3 a genuine 33.6x slash-word, p04 31.6x rules. REJECTED.
#   * max internal CC gap: collapsed maxgap 8px == the ordinary
#     letter-gap ceiling 8px on these pages. REJECTED alone.
#   * pitch (width per CC) / mean gap / ink fraction: genuine long
#     words rank ABOVE the known collapse on every one (e.g. a genuine
#     bold slash-word at 10.2x med_h pitch vs collapsed 2.0x). REJECTED.
#   * line-ratio alone (box width / its line's span): genuine
#     single words reach 0.74 (p13 "PREFERENTIAL)", p3 GSTIN) while a
#     genuine collapse sits at 0.58 (p20 L56). REJECTED alone.
#
# The RULE that survives (all three conditions together):
#   T3 flags a word box iff ALL hold:
#     (a) w > 12 x med_h AND 0.35 x med_h < h <= 2.5 x med_h
#         (single-line text; rules and multi-row blobs excluded), AND
#     (b) the box covers >= 0.55 of its own line's span AND its line
#         has <= 2 word boxes (the box IS the line, not one word of it),
#         AND
#     (c) the largest internal Otsu-CC gap inside the box is >= 6 px
#         (the box holds word-gaps, not only letter-gaps).
#   Principle: no ONE ink statistic separates a word from a line on
#   these pages (letter-gaps and word-gaps overlap at 300 DPI on small
#   print) -- but a box that IS its line (b) AND contains word-sized
#   gaps (c) cannot be one word. Each leg is necessary: (b) without (c)
#   flags genuine long words on short lines; (c) without (b) flags
#   "CERTIFICATE"-style wide-spaced single words.
#   Measured separation (33 R20-baseline pages + 33 nodp pages):
#   8 baseline flags, ALL eye-verified multi-word (8/8 TP, 0 FP);
#   nodp +1 flag, the known p21 collapse. Nearest genuine maxgap 5px
#   (p25 slash-word, p27, p3) vs nearest flagged maxgap 6px -- a THIN
#   1px margin, reported honestly, not a derived principle.
#   KNOWN recall gap: the rule MISSES multi-word boxes whose line has
#   >= 3 words (ratio diluted, e.g. p20 [1282,775,1697,793],
#   [712,2074,1099,2092]) and boxes with maxgap 5px (p20 [626,746,
#   819,764] "AHMEDABAD 382..."). Measured recall on eye-verified
#   p20 multi-word boxes: 8 flagged / 11+ certain-or-probable.
#   T3 is a REFUSE (like T1/T2): a collapsed box makes the live page
#   uneditable for that line. Consequence, measured: the R20 baseline
#   gate moves 23/2 -> 22/3 (p20 flips -- its 8 collapsed boxes are
#   genuine, eye-verified; the task's "(there should be none)"
#   assumption is refuted by measurement, see TRACK-REPORT.md §2).
T3_MIN_W_MED = 12.0     # (a) width in med_h
T3_MIN_H_MED = 0.35     # (a) height floor (rules excluded)
T3_MAX_H_MED = 2.5      # (a) height ceiling (multi-row blobs excluded)
T3_MIN_LINE_RATIO = 0.55  # (b) box width / its line's span
T3_MAX_WORDS_ON_LINE = 2  # (b) words on the line
T3_MIN_MAX_GAP_PX = 6   # (c) largest internal CC gap, px

# --- ROUND 22 (Track T3): Path A' + Path B + tight-joiner guard --------
# Path A (above, unchanged) catches 8/11 of the eye-verified p20
# collapses. Its two named recall gaps are repaired by two further
# legs, both measured on all 33 pages (108 wide boxes) before adoption:
#
#   Path A' (1px-margin repair): (a) + (b) + maxgap == 5 + maxgap >=
#   3 x line_med_letter_gap (non-negative median gap of the OTHER
#   words on the line). On p20 [626,746,819,764] "AHMEDABAD 382110"
#   the line has a 1px letter-gap ruler (line_med 1.0) while the box's
#   maxgap is 5px = 5.0x the ruler -- a whole line of letter-gaps at
#   5x the line's own letter spacing is not one word. Fires on
#   EXACTLY 1 box across all 33 pages ([626,746]): perfect separation.
#   This is NOT "lower the threshold to 5px" -- the 5px alone is
#   allowed only when the line's own letter gaps are >= 3x smaller.
#
#   Path B (internal split): split the box's CCs at gaps >= thr =
#   max(5, F x trim_med), F = 1.70, trim_med = median gap excluding
#   the 2 largest (fallback: the line's letter-gap median; for <=2
#   gaps, thr = max(5, 1.5 x line_med)). Hyphen-adjacent gaps never
#   split. Flag iff >= 2 word-like groups, where a group is word-like
#   iff (n_cc >= 2 and w >= 20px) OR (one CC w >= 2.5 x med_h --
#   catching fused words like "EXPORTER"/"REFERENCE" that the
#   segmenter merged into one CC). Principle: a single word's
#   internal gaps cluster near the box's own letter-gap median, while
#   a collapsed line hides 2+ word-sized clusters separated by gaps
#   far above that median; the threshold is RELATIVE to the box's own
#   gap distribution, not an absolute px value.
#   Measured factor window: F in (5/3, 7/4] = (1.667, 1.75] gives
#   identical results -- the lower bound is set by DECLARATIONS /
#   COMMMERCIAL (maxgap/trim = 5/3 = 1.667, must NOT split) and the
#   upper bound by [712,2074] "SYNTHETIC RESIN / LACQUER COATED"
#   (7/4 = 1.75, must split). F = 1.70 sits inside with margin on
#   both sides; like R19's 0.92, a narrow measured interval -- honest
#   knife-edge, reported as such, not a derived principle.
#
#   Tight-joiner guard (Path B only): a box that holds ONE token
#   joined by punctuation -- phone "033-22851286", emails
#   "mataplt@matagroup.in" / "info@ravirajfoils.com", URLs
#   "http://www.ravirajfoils.com" -- has the same internal gaps as a
#   collapse (the split sees word-like groups) but is NOT a collapse.
#   B does NOT flag a box that contains a TIGHT JOINER: a
#   punctuation-shaped CC with CCs on both sides whose gaps on BOTH
#   sides are < thr (it joins its neighbours with no space):
#     hyphen-like: h < 0.55 x med_h, w >= 1.5 x h, w >= 0.4 x med_h,
#       and vertically centred (|y_c - band_c| <= 0.25 x med_h);
#     slash-like:  h >= 0.8 x med_h, w <= 0.5 x med_h, fill <= 0.30
#       (a diagonal stroke: "/" fill 0.17-0.21 vs "t" 0.40,
#       "l"/"1" 0.76-0.85 -- measured);
#     at-like:     h >= 1.5 x med_h, 1.5 x med_h <= w <= 2.5 x med_h,
#       1 <= enclosed holes <= 2 (one @ glyph; the upper width bound
#       and holes <= 2 exclude a fused word such as p01 "today",
#       w = 3.5 x med_h with 3 holes, which otherwise mimics @).
#   Tightness is essential: a LOOSE @ or / with word gaps on both
#   sides ("today @ Rs.", "RESIN / LACQUER") is a real word separator
#   inside a collapse, and the guard correctly does NOT trigger there.
#   Measured: the guard blocks exactly the 7 genuine joined-token
#   boxes (phone + 2 emails + 4 URLs) and ZERO eye-verified
#   collapses across all 33 pages.
#
#   Measured result (R22 Track T3, eye-verified set of 35 collapses
#   and 16 genuine controls on 33 pages): A|A'|B = 34/35 recall, 0 FP.
#   The single miss is p20 [557,661,986,678] (whole-line fusion,
#   maxgap 2px, only 3 CCs) -- NO gap-based signal can catch it; the
#   segmenter must fix it, not the eye. The task's 11-set: 11/11.
#   KNOWN FN modes: a hyphenated-word collapse ("WELL-KNOWN BRAND")
#   would be guarded as one joined token (0 occurrences on 33 pages);
#   a short tall+holey fused word ("joy") could false-trigger the
#   at-like shape (0 occurrences); the slash fill threshold is
#   validated at large print (med_h >= 20) -- small-print "/" fill is
#   unmeasured. Gate consequence (measured, honest): p01 and p21 flip
#   ALLOW -> REFUSE because the eye now sees REAL collapses there
#   (p01 x3, p21 x1, all eye-verified) -- the task's "must stay 24/1"
#   assumption is refuted by measurement, see TRACK-REPORT.md §5,
#   exactly as R21's T3 refuted the same assumption for p20.
T3_SPLIT_FACTOR = 1.70        # Path B: thr = max(5, 1.70 x trim_med)
T3_SPLIT_FLOOR_PX = 5         # Path B: thr never below 5px
T3_SPLIT_SMALLN_FACTOR = 1.5  # Path B, <=2 gaps: thr = max(5, 1.5 x line_med)
T3_APRIME_LINE_FACTOR = 3.0   # Path A': maxgap >= 3 x line_med_letter_gap
T3_WORD_MIN_W_PX = 20         # Path B: word-like group min width (n_cc>=2)
T3_FUSED_WORD_MIN_W_MED = 2.5  # Path B: single fused CC min width (x med_h)


def _cc_list_for_t3(gray):
    """Page Otsu CCs (area>=4), same recipe as uncovered_clusters."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, _lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    return [(int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4]))
            for s in stats[1:] if int(s[4]) >= 4]


def _cc_holes_for_t3(gray):
    """Enclosed-hole count per Otsu CC, keyed by (x, y, w, h).

    Holes (RETR_CCOMP children) are what distinguish the @ glyph
    (1-2 holes) from letters and from fused words (3 holes). One extra
    connected-components pass per page; only used by the Path B
    tight-joiner guard."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    out = {}
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if area < 4:
            continue
        m = (lab[y:y + h, x:x + w] == i).astype("uint8")
        cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        holes = int((hier[0][:, 3] != -1).sum()) if hier is not None else 0
        out[(x, y, w, h)] = holes
    return out


def _max_internal_gap(ccs, box):
    """Largest x-gap between consecutive CCs (centre inside box),
    walking with a running right edge. Same semantics as the R21
    track-gate probe (gap_probe2.py / decision_table)."""
    x0, y0, x1, y1 = box
    iv = sorted((cx, cx + cw) for (cx, cy, cw, ch, a) in ccs
                if x0 <= cx + cw / 2 <= x1 and y0 <= cy + ch / 2 <= y1)
    if len(iv) < 2:
        return 0, len(iv)
    gaps = []
    right = iv[0][1]
    for a, b in iv[1:]:
        gaps.append(a - right)
        right = max(right, b)
    return max(gaps), len(iv)


def _box_ccs_t3(ccs, box):
    """CCs whose centre lies inside the box, in x order, as
    (x0, x1, y0, y1, w, h, fill, holes)."""
    x0, y0, x1, y1 = box
    iv = []
    for (cx, cy, cw, ch, a) in ccs:
        if x0 <= cx + cw / 2 <= x1 and y0 <= cy + ch / 2 <= y1:
            iv.append((cx, cx + cw, cy, cy + ch, cw, ch,
                       a / max(1, cw * ch), 0))
    iv.sort(key=lambda t: t[0])
    return iv


def _nonneg_gaps_t3(iv):
    """Non-negative x-gaps between consecutive CCs (running right
    edge). Overlapping (negative) gaps are ink fusion, not a space --
    they carry no letter/word-gap signal and are dropped, as in the
    R22 probe2 measurement."""
    gaps = []
    if len(iv) < 2:
        return gaps
    right = iv[0][1]
    for t in iv[1:]:
        gaps.append(t[0] - right)
        right = max(right, t[1])
    return [gp for gp in gaps if gp >= 0]


def _trim_med_t3(gaps):
    """Median gap excluding the 2 largest (the word gaps themselves):
    the box's own letter-gap ruler. None when <= 2 gaps."""
    if len(gaps) <= 2:
        return None
    rest = sorted(gaps)[:-2]
    return float(np.median(rest))


def _split_groups_t3(iv, med_h, thr):
    """Split the box's CCs at gaps >= thr. A gap adjacent to a
    hyphen-like CC (short/wide, h < 0.55 x med_h, w >= 1.5 x h,
    w >= 0.4 x med_h) never splits -- a hyphen joins, it does not
    separate words. Returns (groups, n_word_like) where a group is
    word-like iff (n_cc >= 2 and w >= 20px) or (one CC
    w >= 2.5 x med_h, a fused word the segmenter merged)."""
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
        if (len(gr) >= 2 and w >= T3_WORD_MIN_W_PX) or \
           (len(gr) == 1 and w >= T3_FUSED_WORD_MIN_W_MED * med_h):
            n_wl += 1
    return groups, n_wl


def _is_hyphen_like_t3(c, med_h, band_c):
    """Short, wide, vertically centred CC -- the '-' in a phone number."""
    return (c[5] < 0.55 * med_h and c[4] >= 1.5 * c[5]
            and c[4] >= 0.4 * med_h
            and abs((c[2] + c[3]) / 2 - band_c) <= 0.25 * med_h)


def _is_slash_like_t3(c, med_h):
    """Tall, thin, low-fill CC -- the '/' in a URL (diagonal stroke).
    Measured fill: '/' 0.17-0.21, 't' 0.40, 'l'/'1' 0.76-0.85."""
    return (c[5] >= 0.8 * med_h and c[4] <= 0.5 * med_h
            and c[6] <= 0.30)


def _is_at_like_t3(c, med_h):
    """One @ glyph: tall + wide, 1-2 enclosed holes. The width upper
    bound and holes <= 2 exclude fused words (p01 'today': w = 3.5 x
    med_h, 3 holes)."""
    return (c[5] >= 1.5 * med_h
            and 1.5 * med_h <= c[4] <= 2.5 * med_h
            and 1 <= c[7] <= 2)


def _has_tight_joiner_t3(iv, med_h, band_c, thr):
    """True iff some interior CC is a punctuation joiner with gaps
    < thr on BOTH sides (it joins its neighbours with no space, so
    the box holds one joined token, not separate words). Tightness is
    what saves a loose separator inside a real collapse
    ('today @ Rs.', 'RESIN / LACQUER')."""
    if len(iv) < 3:
        return False
    for k in range(1, len(iv) - 1):
        c = iv[k]
        left_gap = c[0] - max(t[1] for t in iv[:k])
        right_gap = iv[k + 1][0] - c[1]
        if not (0 <= left_gap < thr and 0 <= right_gap < thr):
            continue
        if _is_hyphen_like_t3(c, med_h, band_c):
            return True
        if _is_slash_like_t3(c, med_h):
            return True
        if _is_at_like_t3(c, med_h):
            return True
    return False


def _cc_list_for_t3(gray):
    """Page Otsu CCs (area>=4), same recipe as uncovered_clusters."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, _lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    return [(int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4]))
            for s in stats[1:] if int(s[4]) >= 4]


def _max_internal_gap(ccs, box):
    """Largest x-gap between consecutive CCs (centre inside box),
    walking with a running right edge. Same semantics as the R21
    track-gate probe (gap_probe2.py / decision_table)."""
    x0, y0, x1, y1 = box
    iv = sorted((cx, cx + cw) for (cx, cy, cw, ch, a) in ccs
                if x0 <= cx + cw / 2 <= x1 and y0 <= cy + ch / 2 <= y1)
    if len(iv) < 2:
        return 0, len(iv)
    gaps = []
    right = iv[0][1]
    for a, b in iv[1:]:
        gaps.append(a - right)
        right = max(right, b)
    return max(gaps), len(iv)



# --- ROUND 23 (Track T3): Path C -- fully-fused line, no gap signal ----
# The R22 eye's only miss, p20 [557,661,986,678] ("BENEFICIARY /
# MANUFACTURER / EXPORTER / SHIPPER", 4 words), is 3 CCs of 117-158px
# (8.4-11.3x med_h) with maxgap 2px: NO gap-based leg (A, A', B) can
# see it. Path C judges the box's INK TOPOLOGY, not its gaps:
#   (i)   NO letter-sized CC: every CC in the box is >= 2.0x med_h
#         wide. Principle: no single letter is 2x med_h wide (widest
#         letters m/w are ~1.0-1.3x); a box with zero letter-sized
#         CCs cannot be one word rendered in the page's font.
#         Measured margin (108 (a)-boxes, 33 pages, BOTH seg sets):
#         target min CC 8.36x med_h; nearest non-target 1.55x --
#         the 2.0 boundary sits in the empty interval [1.55, 8.36],
#         a 5.4x margin, NOT a knife-edge. The (i) leg ALONE fires
#         only on the target across all 33 pages x 2 seg sets.
#   (ii)  fused union cover >= 0.5: the fused CCs (clipped to the
#         box) must cover at least half the box width (majority --
#         a guard, not fitted; target 0.993).
#   (iii) longest zero-ink run <= 2px: the box holds no gap even
#         letter-gap-sized enough to be a candidate split point, so
#         A/A'/B have nothing to judge -- the line is fully fused.
#         (iii) changes zero outcomes on 33 pages; it is
#         defense-in-depth, stated honestly.
# No tight-joiner guard: the target IS slash-joined, but its slashes
# live INSIDE the fused CCs (no separate joiner CC exists to detect);
# genuine joined tokens (phone/email/URL) have letter-sized CCs and
# are excluded by (i). A dust speck (area>=4) inside the box would
# veto C -- conservative by design (a miss then belongs to the
# segmenter track, not to a false flag).
# RESEARCH23 signals tested and REJECTED for this box (see
# TRACK-REPORT.md): count-driven expected-n (US5253304: 9.13 vs true
# 4, 2.28x over; genuine controls 3.58-8.93 -- no separation; and its
# own rule refuses to cut: 0 good valleys for 8 wanted cuts),
# bridge-strength greyscale (EP0780782: target min-grey 210-225 vs
# genuine 151-255 -- overlap), white-column W-W_core (all 1.0
# everywhere -- no separation), reservoir pocket ratio (target 8.0
# vs genuine max 3.0 BUT stamp-overlapped box 30.0 -- false
# positive, so not a deciding vote).
T3_FUSED_MIN_W_MED = 2.0   # Path C (i): letter-sized CC ceiling (x med_h)
T3_FUSED_MIN_COVER = 0.5   # Path C (ii): fused union cover floor
T3_FUSED_MAX_GAP_PX = 2    # Path C (iii): longest zero-ink run, px


def _cc_list_for_t3(gray):
    """Page Otsu CCs (area>=4), same recipe as uncovered_clusters."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, _lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    return [(int(s[0]), int(s[1]), int(s[2]), int(s[3]), int(s[4]))
            for s in stats[1:] if int(s[4]) >= 4]


def _cc_holes_for_t3(gray):
    """Enclosed-hole count per Otsu CC, keyed by (x, y, w, h).

    Holes (RETR_CCOMP children) are what distinguish the @ glyph
    (1-2 holes) from letters and from fused words (3 holes). One extra
    connected-components pass per page; only used by the Path B
    tight-joiner guard."""
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    out = {}
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if area < 4:
            continue
        m = (lab[y:y + h, x:x + w] == i).astype("uint8")
        cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        holes = int((hier[0][:, 3] != -1).sum()) if hier is not None else 0
        out[(x, y, w, h)] = holes
    return out


def _max_internal_gap(ccs, box):
    """Largest x-gap between consecutive CCs (centre inside box),
    walking with a running right edge. Same semantics as the R21
    track-gate probe (gap_probe2.py / decision_table)."""
    x0, y0, x1, y1 = box
    iv = sorted((cx, cx + cw) for (cx, cy, cw, ch, a) in ccs
                if x0 <= cx + cw / 2 <= x1 and y0 <= cy + ch / 2 <= y1)
    if len(iv) < 2:
        return 0, len(iv)
    gaps = []
    right = iv[0][1]
    for a, b in iv[1:]:
        gaps.append(a - right)
        right = max(right, b)
    return max(gaps), len(iv)


def _box_ccs_t3(ccs, box):
    """CCs whose centre lies inside the box, in x order, as
    (x0, x1, y0, y1, w, h, fill, holes)."""
    x0, y0, x1, y1 = box
    iv = []
    for (cx, cy, cw, ch, a) in ccs:
        if x0 <= cx + cw / 2 <= x1 and y0 <= cy + ch / 2 <= y1:
            iv.append((cx, cx + cw, cy, cy + ch, cw, ch,
                       a / max(1, cw * ch), 0))
    iv.sort(key=lambda t: t[0])
    return iv


def _nonneg_gaps_t3(iv):
    """Non-negative x-gaps between consecutive CCs (running right
    edge). Overlapping (negative) gaps are ink fusion, not a space --
    they carry no letter/word-gap signal and are dropped, as in the
    R22 probe2 measurement."""
    gaps = []
    if len(iv) < 2:
        return gaps
    right = iv[0][1]
    for t in iv[1:]:
        gaps.append(t[0] - right)
        right = max(right, t[1])
    return [gp for gp in gaps if gp >= 0]


def _trim_med_t3(gaps):
    """Median gap excluding the 2 largest (the word gaps themselves):
    the box's own letter-gap ruler. None when <= 2 gaps."""
    if len(gaps) <= 2:
        return None
    rest = sorted(gaps)[:-2]
    return float(np.median(rest))


def _split_groups_t3(iv, med_h, thr):
    """Split the box's CCs at gaps >= thr. A gap adjacent to a
    hyphen-like CC (short/wide, h < 0.55 x med_h, w >= 1.5 x h,
    w >= 0.4 x med_h) never splits -- a hyphen joins, it does not
    separate words. Returns (groups, n_word_like) where a group is
    word-like iff (n_cc >= 2 and w >= 20px) or (one CC
    w >= 2.5 x med_h, a fused word the segmenter merged)."""
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
        if (len(gr) >= 2 and w >= T3_WORD_MIN_W_PX) or \
           (len(gr) == 1 and w >= T3_FUSED_WORD_MIN_W_MED * med_h):
            n_wl += 1
    return groups, n_wl


def _is_hyphen_like_t3(c, med_h, band_c):
    """Short, wide, vertically centred CC -- the '-' in a phone number."""
    return (c[5] < 0.55 * med_h and c[4] >= 1.5 * c[5]
            and c[4] >= 0.4 * med_h
            and abs((c[2] + c[3]) / 2 - band_c) <= 0.25 * med_h)


def _is_slash_like_t3(c, med_h):
    """Tall, thin, low-fill CC -- the '/' in a URL (diagonal stroke).
    Measured fill: '/' 0.17-0.21, 't' 0.40, 'l'/'1' 0.76-0.85."""
    return (c[5] >= 0.8 * med_h and c[4] <= 0.5 * med_h
            and c[6] <= 0.30)


def _is_at_like_t3(c, med_h):
    """One @ glyph: tall + wide, 1-2 enclosed holes. The width upper
    bound and holes <= 2 exclude fused words (p01 'today': w = 3.5 x
    med_h, 3 holes)."""
    return (c[5] >= 1.5 * med_h
            and 1.5 * med_h <= c[4] <= 2.5 * med_h
            and 1 <= c[7] <= 2)


def _has_tight_joiner_t3(iv, med_h, band_c, thr):
    """True iff some interior CC is a punctuation joiner with gaps
    < thr on BOTH sides (it joins its neighbours with no space, so
    the box holds one joined token, not separate words). Tightness is
    what saves a loose separator inside a real collapse
    ('today @ Rs.', 'RESIN / LACQUER')."""
    if len(iv) < 3:
        return False
    for k in range(1, len(iv) - 1):
        c = iv[k]
        left_gap = c[0] - max(t[1] for t in iv[:k])
        right_gap = iv[k + 1][0] - c[1]
        if not (0 <= left_gap < thr and 0 <= right_gap < thr):
            continue
        if _is_hyphen_like_t3(c, med_h, band_c):
            return True
        if _is_slash_like_t3(c, med_h):
            return True
        if _is_at_like_t3(c, med_h):
            return True
    return False


def _fused_union_cover_t3(iv, box):
    """x-coverage (clipped to the box) of CCs wider than
    T3_FUSED_MIN_W_MED x med_h, as a fraction of box width."""
    x0 = box[0]
    ww = box[2] - box[0]
    if ww <= 0:
        return 0.0
    ivs = sorted((max(0, t[0] - x0), min(ww, t[1] - x0)) for t in iv)
    if not ivs:
        return 0.0
    tot = 0
    cs, ce = ivs[0]
    for a, b in ivs[1:]:
        if a <= ce:
            ce = max(ce, b)
        else:
            tot += ce - cs
            cs, ce = a, b
    tot += ce - cs
    return tot / ww


def _path_c_fused_t3(iv, box, med_h, max_gap):
    """Path C: True iff the box is a fully-fused line -- every CC is
    fused-width (no letter-sized CC), the fused CCs cover >= half
    the box width, and no zero-ink run longer than
    T3_FUSED_MAX_GAP_PX exists inside. iv is _box_ccs_t3 output
    (x0, x1, y0, y1, w, h, fill, holes); max_gap is the longest
    internal CC gap (== longest zero-ink run)."""
    if not iv:
        return False
    fused = [t for t in iv if t[4] >= T3_FUSED_MIN_W_MED * med_h]
    if len(fused) != len(iv):
        return False  # a letter-sized CC exists: this holds a real word
    if _fused_union_cover_t3(fused, box) < T3_FUSED_MIN_COVER:
        return False
    if max_gap > T3_FUSED_MAX_GAP_PX:
        return False
    return True


# --- ROUND 25 (Track gate): T4 over-split eye ---------------------------
# R24 §6 measured the blind spot: T3 catches whole-line COLLAPSE (too
# few boxes) but not OVER-SPLIT (too many). The bridge track cut p20's
# fused line into 6 wrong pieces and the seam track into 8, both 0/4
# true words -- and the gate said ALLOW both times (24/1), because a
# shredded line has no piece wide enough (>= 12x med_h) for T3 to
# examine. The gate's number is not truth; word identity is truth.
#
# T4 judges the SPLIT, not the image alone. It re-fuses runs of
# abutting pieces and asks whether the re-fused run is the same
# fully-fused line T3 Path C already knows -- and whether the cuts
# inside it went through letter gaps (wrong) or through the slash
# strokes (right):
#   (1) RUN: consecutive words on one text line, each gap <= 2px and
#       y-bands overlapping >= half the shorter height, each piece
#       extending the run rightward. (Bridge/seam pieces abut, gap 0;
#       the 2px join is Path C (iii)'s own scale. Genuine word gaps
#       <= 2px are common -- 355 on 33 baseline pages -- so the join
#       alone proves nothing; legs (2)+(3) do the work.)
#   (2) RE-FUSE: the run's union box must pass Path C's own legs:
#       width >= 12x med_h, single-line height, EVERY Otsu CC in the
#       union >= 2.0x med_h wide (no letter-sized CC -- measured empty
#       interval [1.55, 8.36], same as Path C), fused cover >= 0.5,
#       longest internal CC gap <= 2px. A run of genuine words fails
#       (2) because its letters are letter-sized CCs.
#   (3) WHITE-CUT VOTE: each internal boundary column x (the cut edge,
#       left piece's x1) must be a slash stroke, not a letter gap. A
#       slash is a full-height diagonal stroke: its column carries
#       Otsu ink in most band rows. Measured on p20 (band 17 rows):
#       the 3 true slash columns read ink frac 0.647 / 0.882 / 0.706;
#       all 12 wrong cuts (5 bridge + 7 seam) read <= 0.529 -- an
#       empty interval (0.529, 0.647), threshold 0.60 at its middle.
#       A boundary with ink frac <= 0.60 is a WHITE cut: the segmenter
#       cut through a letter gap, so the pieces either side cannot
#       both be true words. ONE white cut flags the run (a correct
#       split of a fused line cuts only through slashes; an extra cut
#       anywhere else is over-split by definition).
#   A correct split of the same fused line would pass: its union is
#   Path-C-fused (the image is unchanged) but every boundary reads
#   dark (0.647+), so no flag -- the eye distinguishes a right split
#   from a wrong one, which a bare re-fuse test could not.
#   KNOWN LIMIT (stated, not hidden): the vote reads ONE column, so
#   a correct cut must land within ~+/-1px of the slash centre (the
#   slash's dark span is 6-9 columns wide; a segmenter cutting
#   through the slash lands inside it). A cut 2px+ off centre reads
#   white and would flag -- that cut is misplaced (it cuts letter
#   ink, not the slash), so flagging it is defensible, but the
#   tolerance is narrow and is recorded here.
#   T4 does NOT require the run to be its whole line (T3 leg (b) is
#   deliberately dropped): a fused pair inside a longer line is still
#   over-split if cut through letter gaps; legs (2)+(3) already
#   exclude genuine words.
T4_JOIN_GAP_PX = 2        # (1) max gap between run pieces, px
T4_MIN_RUN_WORDS = 2      # (1) a run needs >= 2 pieces
T4_WHITE_CUT_FRAC = 0.60  # (3) boundary ink frac <= this -> white cut
T4_MIN_Y_OVERLAP = 0.5    # (1) y-band overlap / shorter height


# --- ROUND 26 (Track gate): T5 rule-shred eye ----------------------------
# R25 §6: the fuzzy-vote splitter's guard fires on ANY Path-C-shaped box
# (ww >= 12x med_h, hh <= 3x med_h, all CCs >= 2x med_h, cover >= 0.5,
# max zero-ink run <= 2px) -- and a horizontal RULE is exactly
# Path-C-shaped (p01 rule [1429,1312,1736,1317]: 307x5px, ONE CC,
# 307px = 15.4x med_h). The guard shredded it into 5 pieces and the
# gate said nothing: T3/T4 both exclude rule-shaped boxes, and no eye
# judges a shredded rule. T5 closes that hole.
#
# A box is RULE-LIKE (not text) iff ALL hold (measured probe_a_rule.py,
# 33 baseline pages, 87 wide boxes w >= 12x med_h):
#   (i)   h <= 0.50 x med_h AND w >= 12 x med_h (long, thin);
#   (ii)  ONE Otsu CC spans >= 0.80 of the box width (a rule is one
#         stroke; text is many letter CCs).
#   Measured separation: the joint rule fires on EXACTLY 5 boxes on
#   all 33 pages, and ALL 5 are rules (p01 [1429,1312,1736,1317],
#   p2 [1437,1314,1741,1319], p01 [1150,1145,1438,1151],
#   p2 [1176,1090,1441,1096], p2 [1154,1150,1443,1156]) -- 0 text
#   boxes. The nearest text boxes fail (i): the thinnest genuine
#   text box is 0.94x med_h tall. Two thin non-rule boxes on p04
#   (568x2/3px table lines) fail (ii): dominant CC only 0.014 of
#   width (dashed/dotted rendering) -- correctly excluded.
#   Signals REJECTED as the rule (measured): fill >= 0.8 (rule fill
#   is only 0.60 -- light print leaves 2 of 5 rows grey; 0 text boxes
#   reach 0.8 either, so fill separates nothing here); median
#   per-column ink frac >= 0.8 (rule reads 0.60, text max 1.00 --
#   OVERLAP, the p04 table lines read 1.00); min per-row ink frac
#   (rule reads 0.07 -- the top/bottom rows are grey halo, not ink).
#   The height + dominant-CC pair is the separator, not any ink
#   fraction -- because a rule's identity is its SHAPE (one long
#   thin stroke), not its darkness.
#
# T5 flags a RUN of >= 2 abutting pieces (T4's run construction) whose
# UNION is rule-like: the segmenter cut one rule into pieces. A single
# unshredded rule box never flags (it is not a run). A run of text
# pieces never flags: its union is a text line ~0.9-1.0x med_h tall,
# failing (i). Same guard-side fix belongs in the splitter guard
# (build_fuzzy.py _split_fused_fuzzy): refuse to split a rule-like
# box -- demonstrated in probe_a_guard.py; the gate eye catches it
# after the fact if any future splitter repeats the mistake.
T5_RULE_MAX_H_MED = 0.50   # (i) rule height ceiling (x med_h)
T5_RULE_MIN_W_MED = 12.0   # (i) rule width floor (x med_h)
T5_RULE_MIN_DOM_FRAC = 0.80  # (ii) dominant CC width / box width


def is_rule_like(ccs, box, med_h):
    """True iff the box is a horizontal rule, not text: long, thin,
    one dominant CC. ccs is _cc_list_for_t3 output (x,y,w,h,area)."""
    x0, y0, x1, y1 = box
    ww, hh = x1 - x0, y1 - y0
    if ww < T5_RULE_MIN_W_MED * med_h:
        return False
    if hh > T5_RULE_MAX_H_MED * med_h:
        return False
    iv = _box_ccs_t3(ccs, box)
    if not iv:
        return False
    dom = max(t[4] for t in iv) / float(ww)
    return dom >= T5_RULE_MIN_DOM_FRAC


def ruleshred_candidates(gray, seg):
    """T5: runs of abutting pieces whose union is a rule. Each entry
    carries the run box, piece boxes, and the rule evidence."""
    words = seg["words"]
    med_h = float(seg.get("median_char_h_px", 20))
    ccs = _cc_list_for_t3(gray)
    out = []
    for run in _runs_t4(words):
        x0 = min(w["box"][0] for w in run)
        x1 = max(w["box"][2] for w in run)
        y0 = min(w["box"][1] for w in run)
        y1 = max(w["box"][3] for w in run)
        union = [x0, y0, x1, y1]
        if not is_rule_like(ccs, union, med_h):
            continue
        iv = _box_ccs_t3(ccs, union)
        dom = max(t[4] for t in iv) / float(x1 - x0) if iv else 0.0
        out.append({"box": list(union), "n_pieces": len(run),
                    "piece_boxes": [list(w["box"]) for w in run],
                    "h_med": round((y1 - y0) / med_h, 2),
                    "w_med": round((x1 - x0) / med_h, 1),
                    "dom_cc_frac": round(dom, 3)})
    return out


def _ink_frac_col(ink, x, y0, y1):
    """Otsu-ink fraction of column x over rows [y0, y1). ink is a
    boolean array. Out-of-range x reads 0.0 (no ink)."""
    h = y1 - y0
    if h <= 0 or x < 0 or x >= ink.shape[1]:
        return 0.0
    return float(ink[y0:y1, x].sum()) / h


def _runs_t4(words):
    """Runs of abutting same-line pieces, in x order. Words are
    scanned in x0 order; a word joins the run whose last piece it
    abuts (gap <= T4_JOIN_GAP_PX, y-overlap >= T4_MIN_Y_OVERLAP of
    the shorter height, and it extends the run rightward), else it
    starts a new run. Non-joining words (other rows interleaved in
    x order) are skipped, not run-breakers."""
    order = sorted(words, key=lambda w: w["box"][0])
    runs = []
    for w in order:
        b = w["box"]
        best = None
        for ri, r in enumerate(runs):
            last = r[-1]["box"]
            gap = b[0] - last[2]
            if gap > T4_JOIN_GAP_PX:
                continue
            if b[2] <= last[2]:
                continue  # must extend the run rightward
            ov = min(b[3], last[3]) - max(b[1], last[1])
            if ov < T4_MIN_Y_OVERLAP * min(b[3] - b[1], last[3] - last[1]):
                continue
            if best is None or last[2] > runs[best][-1]["box"][2]:
                best = ri
        if best is None:
            runs.append([w])
        else:
            runs[best].append(w)
    return [r for r in runs if len(r) >= T4_MIN_RUN_WORDS]


def oversplit_candidates(gray, seg):
    """T4: return the list of over-split runs (see rule above).
    Each entry carries the run box, piece boxes/widths, and the
    per-boundary ink fractions with the white/dark vote."""
    words = seg["words"]
    med_h = float(seg.get("median_char_h_px", 20))
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ink = bw > 0
    ccs = _cc_list_for_t3(gray)
    out = []
    for run in _runs_t4(words):
        x0 = min(w["box"][0] for w in run)
        x1 = max(w["box"][2] for w in run)
        y0 = min(w["box"][1] for w in run)
        y1 = max(w["box"][3] for w in run)
        ww, hh = x1 - x0, y1 - y0
        if ww < T3_MIN_W_MED * med_h:
            continue
        if not (T3_MIN_H_MED * med_h < hh <= T3_MAX_H_MED * med_h):
            continue
        if is_rule_shaped(ww, hh, ww * hh):
            continue
        union = [x0, y0, x1, y1]
        mg, ncc = _max_internal_gap(ccs, union)
        iv = _box_ccs_t3(ccs, union)
        if not _path_c_fused_t3(iv, union, med_h, mg):
            continue  # genuine words: letter-sized CCs inside
        bounds = []
        for a, b in zip(run, run[1:]):
            bx = a["box"][2]  # cut edge = left piece's x1
            fr = _ink_frac_col(ink, bx, y0, y1)
            bounds.append({"x": int(bx), "ink_frac": round(fr, 3),
                           "white": bool(fr <= T4_WHITE_CUT_FRAC)})
        whites = [bd for bd in bounds if bd["white"]]
        if not whites:
            continue  # correct split: every cut through a slash
        out.append({"box": list(union), "n_pieces": len(run),
                    "piece_boxes": [list(w["box"]) for w in run],
                    "piece_w_med": [round((w["box"][2] - w["box"][0]) / med_h, 2)
                                    for w in run],
                    "w_med": round(ww / med_h, 1),
                    "min_cc_w_med": round(min([t[4] for t in iv], default=0) / med_h, 2) if iv else 0.0,
                    "fus_cover": round(_fused_union_cover_t3([t for t in iv if t[4] >= T3_FUSED_MIN_W_MED * med_h], union), 3) if iv else 0.0,
                    "max_gap_px": int(mg),
                    "boundaries": bounds,
                    "n_white_cuts": len(whites)})
    return out


def collapse_candidates(gray, seg):
    """T3: return the list of collapsed-line boxes (see rule above).
    Geometry only, no OCR. Returns dicts with the measured evidence
    plus 'path': 'A' (R21 rule, unchanged), \"A'\" (1px-margin repair)
    or 'B' (internal split, joiner-guarded). A box flagged by more
    than one leg reports the first in the order A, A', B."""
    words = seg["words"]
    med_h = float(seg.get("median_char_h_px", 20))
    ccs = _cc_list_for_t3(gray)
    holes = _cc_holes_for_t3(gray)
    # per-word non-negative gaps (for the line letter-gap ruler)
    wgaps = {}
    for idx, w in enumerate(words):
        wgaps[idx] = _nonneg_gaps_t3(_box_ccs_t3(ccs, w["box"]))
    page_med = float(np.median([gp for vs in wgaps.values() for gp in vs])) \
        if any(wgaps.values()) else None
    lines = {}
    for w in words:
        ln = w.get("line")
        if ln is None:
            continue  # no line evidence -> no T3 verdict for this word
        lines.setdefault(ln, []).append(w)
    widx = {id(w): i for i, w in enumerate(words)}
    out = []
    for ln, ws in lines.items():
        span = max(w["box"][2] for w in ws) - min(w["box"][0] for w in ws)
        if span <= 0:
            continue
        for w in ws:
            b = w["box"]
            ww, hh = b[2] - b[0], b[3] - b[1]
            if ww < T3_MIN_W_MED * med_h:
                continue
            if not (T3_MIN_H_MED * med_h < hh <= T3_MAX_H_MED * med_h):
                continue
            if is_rule_shaped(ww, hh, ww * hh):
                continue
            ratio = ww / span
            # --- Path A (R21, unchanged) ---
            path = None
            mg, ncc = _max_internal_gap(ccs, b)
            if ratio >= T3_MIN_LINE_RATIO and len(ws) <= T3_MAX_WORDS_ON_LINE \
                    and mg >= T3_MIN_MAX_GAP_PX:
                path = "A"
            if path is None:
                # line letter-gap ruler: median of the OTHER words'
                # non-negative gaps on this line (page fallback)
                others = []
                for w2 in ws:
                    if w2 is not w:
                        others.extend(wgaps[widx[id(w2)]])
                line_med = float(np.median(others)) if others else page_med
                iv = _box_ccs_t3(ccs, b)
                iv = [(t[0], t[1], t[2], t[3], t[4], t[5], t[6],
                       holes.get((t[0], t[2], t[4], t[5]), 0)) for t in iv]
                gaps = _nonneg_gaps_t3(iv)
                trim = _trim_med_t3(gaps)
                if trim is None:
                    thr = max(T3_SPLIT_FLOOR_PX,
                              T3_SPLIT_SMALLN_FACTOR * line_med) \
                        if line_med is not None else float(T3_SPLIT_FLOOR_PX)
                else:
                    thr = max(T3_SPLIT_FLOOR_PX,
                              T3_SPLIT_FACTOR * trim)
                # --- Path A' (1px-margin repair) ---
                if (ratio >= T3_MIN_LINE_RATIO
                        and len(ws) <= T3_MAX_WORDS_ON_LINE
                        and mg == 5 and line_med is not None
                        and mg >= T3_APRIME_LINE_FACTOR * line_med):
                    path = "A'"
                # --- Path B (internal split, joiner-guarded) ---
                if path is None:
                    _groups, n_wl = _split_groups_t3(iv, med_h, thr)
                    if n_wl >= 2:
                        band_c = (b[1] + b[3]) / 2
                        if not _has_tight_joiner_t3(iv, med_h, band_c, thr):
                            path = "B"
                # --- Path C (Round 23: fully-fused line, ink topology) ---
                if path is None and _path_c_fused_t3(iv, b, med_h, mg):
                    path = "C"
            if path is None:
                continue
            _iv_ev = _box_ccs_t3(ccs, b)
            out.append({"box": list(b), "line": ln, "w_med": round(ww / med_h, 1),
                        "h_px": hh, "line_ratio": round(ratio, 2),
                        "n_words_on_line": len(ws), "max_gap_px": int(mg),
                        "n_cc": int(ncc), "path": path,
                        "min_cc_w_med": round(min([t[4] for t in _iv_ev], default=0) / med_h, 2) if _iv_ev else 0.0,
                        "fus_cover": round(_fused_union_cover_t3([t for t in _iv_ev if t[4] >= T3_FUSED_MIN_W_MED * med_h], b), 3) if _iv_ev else 0.0})
    return out


def check_dp_integrity(segmenter_dir):
    """T3-integrity pre-flight (R20 §11.b, second layer): the segmenter
    that produced a seg batch must have had rhythm-DP available. If
    rhythm_dp.py is missing (or unimportable) next to the segmenter,
    DP silently never runs and whole lines can collapse with the gate
    none the wiser. Returns (ok, detail). This is a fact about the
    pipeline, not a measurement -- 0 false positives by construction.
    The gate() itself does not know the segmenter dir; the RUNNER calls
    this before scoring and aborts loudly on failure."""
    import importlib.util
    import os as _os
    detail = {"segmenter_dir": segmenter_dir}
    rp = _os.path.join(segmenter_dir, "rhythm_dp.py")
    detail["rhythm_dp_exists"] = _os.path.exists(rp)
    if not detail["rhythm_dp_exists"]:
        return False, detail
    try:
        spec = importlib.util.spec_from_file_location("_r21_rhythm_dp", rp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        detail["rhythm_dp_imports"] = hasattr(mod, "rhythm_dp_words")
        detail["has_rhythm_dp_words"] = detail["rhythm_dp_imports"]
        return detail["rhythm_dp_imports"], detail
    except Exception as e:  # noqa: BLE001 -- any import failure = DP dead
        detail["rhythm_dp_imports"] = False
        detail["import_error"] = str(e)[:200]
        return False, detail


def gate(img, seg):
    """Returns (verdict, details). verdict: ALLOW or REFUSE."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    words = seg["words"]
    med_h = float(seg.get("median_char_h_px", 20))
    sig_y = int(detect_sig_y_gate(gray, h))
    sig_y_v4 = int(detect_sig_y(gray, h))
    logo_rect, _li = detect_logo_rect(gray)
    seal_boxes = detect_seal_regions(img, gray)
    reasons = []

    # ---- T1: core-outside ----
    lab, stats = core_ccs(gray)
    assign, ambiguous = _assign_cores_min(lab, stats, words)
    worst = []
    for i, wi in assign.items():
        if wi < 0:
            continue  # -1 unassigned, -2 ambiguous/fused: T1 cannot judge them
        x, y, cw, ch, area = (int(v) for v in stats[i])
        if cw > 120 or ch > 80:
            continue  # band/rule-sized core, not a letter core (R17 cal.)
        if cw > 60 or area > 600:
            continue  # letter-core shape (R17 cal.): the rav-p3 stamp core
        # is 99x31 / 860px and sticks 24px out of a logo-fragment box —
        # a graphic, not a letter; letter cores are <=~40px wide, <=400px
        b = words[wi]["box"]
        # core pixels inside word box (+2px pad)
        x0, y0 = max(0, b[0] - 2), max(0, b[1] - 2)
        x1, y1 = min(w, b[2] + 2), min(h, b[3] + 2)
        core_mask = (lab[y:y + ch, x:x + cw] == i)
        total = int(core_mask.sum())
        if total == 0 or total < 100:
            continue  # <100px cores are halftone dots / specks (R17 cal.:
        # May dot cores tripping T1 were 12-85px; a letter core is 100-400px)
        # pixels of this core inside the box
        ix0, iy0 = max(x, x0), max(y, y0)
        ix1, iy1 = min(x + cw, x1), min(y + ch, y1)
        inside = 0
        if ix1 > ix0 and iy1 > iy0:
            inside = int((lab[iy0:iy1, ix0:ix1] == i).sum())
        out_frac = 1.0 - inside / total
        ext = max(b[0] - x, x + cw - b[2], b[1] - y, y + ch - b[3], 0)
        worst.append((round(out_frac, 3), int(ext), i, wi,
                      [x, y, x + cw, y + ch], b, total))
    worst.sort(reverse=True)
    t1_flags = [t for t in worst if t[0] > CORE_OUT_FRAC and t[1] > CORE_OUT_EXT]
    t1_flags_raw0 = len(t1_flags)  # pre-suppression count (band + seal)
    # --- ROUND 20 TRACK-GATESIDE (d): line-band core-assignment fix ---
    # A core is blamed on its assigned word only if the core's ink belongs
    # to that word's LINE. assign_cores assigns by max pixel overlap with a
    # word BOX, ignoring lines: a signature stroke descending from above
    # the line grazes the word box below and gets assigned to it, and T1
    # then blames the (correct) word for ink that is not its letter.
    # Rule (no new magic number — majority, 0.50): suppress the flag iff
    # MORE THAN HALF of the core's pixels lie outside its word's LINE
    # BAND (min y0 .. max y1 of the words on that line), above or below.
    # A letter of the word lives inside its line band by construction
    # (measured R20-gateside, 27 pages, 99 cores with out_frac>0.25:
    # every REAL T1 flag has above_band == below_band == 0.00 except
    # p01a 0.14 and p13-seal 0.40 — both kept; the p08 stroke core has
    # above_band 0.90. Fill/blue corroborate but are NOT rule inputs:
    # blue would wrongly suppress the p01a logo-"A" core, fill alone
    # would wrongly suppress the p12 "P" core — see TRACK-REPORT.md).
    _band = {}
    for _wd in words:
        _ln = _wd.get("line")
        if _ln is None:
            continue
        _b = _wd["box"]
        if _ln not in _band:
            _band[_ln] = [_b[1], _b[3]]
        else:
            _band[_ln][0] = min(_band[_ln][0], _b[1])
            _band[_ln][1] = max(_band[_ln][1], _b[3])

    def _band_fracs(_i, _wi):
        _x, _y, _cw, _ch, _area = (int(v) for v in stats[_i])
        _m = (lab[_y:_y + _ch, _x:_x + _cw] == _i)
        _tot = int(_m.sum())
        if _tot == 0:
            return 0.0, 0.0
        _b = words[_wi]["box"]
        _ln = words[_wi].get("line")
        _top, _bot = _band.get(_ln, [_b[1], _b[3]])
        _ys = np.nonzero(_m)[0] + _y
        return (round(float((_ys < _top).mean()), 3),
                round(float((_ys > _bot).mean()), 3))

    t1_band_suppressed = []
    t1_flags2 = []
    for t in t1_flags:
        _ab, _bb = _band_fracs(t[2], t[3])
        if max(_ab, _bb) > 0.50:
            t1_band_suppressed.append({"core_box": t[4], "word_idx": t[3],
                                       "word_box": t[5], "outside_frac": t[0],
                                       "above_band": _ab, "below_band": _bb})
        else:
            t1_flags2.append(t)
    t1_flags = t1_flags2
    t1_kept = []
    for t in t1_flags[:10]:
        _cx = (t[4][0] + t[4][2]) / 2
        _cy = (t[4][1] + t[4][3]) / 2
        if _in_seal(seal_boxes, _cx, _cy):
            # R19 Track-sigy: core is a seal-letter fragment, not a real word
            continue
        t1_kept.append(t)
    for t in t1_kept:
        reasons.append({"test": "T1-core-outside",
                        "core_box": t[4], "word_idx": t[3], "word_box": t[5],
                        "outside_frac": t[0], "extension_px": t[1],
                        "core_px": t[6]})
    # ---- T2: word-like uncovered clusters ----
    clusters = uncovered_clusters(gray, words, med_h)
    n_raw = len(clusters)
    t2_flags = []
    for c in clusters:
        x0, y0, x1, y1 = c["box"]
        hh, ww = y1 - y0, x1 - x0
        if y0 >= sig_y:
            continue  # signature zone: mask never touches it
        if logo_rect is not None and x0 >= logo_rect[0] and y0 >= logo_rect[1] and x1 <= logo_rect[2] and y1 <= logo_rect[3]:
            continue  # detected logo rect: mask zeroes it
        if hh >= 150 and ww <= 10:
            continue  # vertical rule
        if ww >= 150 and hh <= 10:
            continue  # horizontal rule
        if not (c["n_cc"] >= 2 and hh >= 12 and ww >= 20 and c["area"] >= 150
                and c["med_cc_h"] >= 10 and c["med_cc_area"] >= 25):
            continue  # fragment / halftone dots / speck
        # overlap with any word box must be < 50% of cluster area
        ov = 0
        for wd in words:
            b = wd["box"]
            ox = max(0, min(x1, b[2]) - max(x0, b[0]))
            oy = max(0, min(y1, b[3]) - max(y0, b[1]))
            ov = max(ov, ox * oy)
        if ov >= 0.5 * ww * hh:
            continue
        # R19 Track-sigy: cluster inside a blue seal region is seal
        # lettering, not a real word
        _ccx = (x0 + x1) / 2
        _ccy = (y0 + y1) / 2
        if _in_seal(seal_boxes, _ccx, _ccy):
            continue
        t2_flags.append(c)
    for c in t2_flags:
        reasons.append({"test": "T2-uncovered-wordlike", "box": c["box"],
                        "n_cc": c["n_cc"], "area": c["area"],
                        "med_cc_h": c["med_cc_h"],
                        "med_cc_area": c["med_cc_area"]})
    # ---- T3: whole-line collapse (Round 21 track-gate) ----
    t3_list = collapse_candidates(gray, seg)
    for c in t3_list:
        reasons.append({"test": "T3-collapse", "box": c["box"],
                        "line": c["line"], "w_med": c["w_med"],
                        "line_ratio": c["line_ratio"],
                        "n_words_on_line": c["n_words_on_line"],
                        "max_gap_px": c["max_gap_px"], "n_cc": c["n_cc"],
                        "path": c["path"]})
    # ---- T4: over-split eye (Round 25 track-gate) ----
    # A run of abutting pieces whose re-fused union is a Path-C
    # fully-fused line, with >= 1 internal cut through a letter gap
    # (white boundary column) instead of through a slash stroke.
    t4_list = oversplit_candidates(gray, seg)
    for c in t4_list:
        reasons.append({"test": "T4-oversplit", "box": c["box"],
                        "n_pieces": c["n_pieces"],
                        "piece_w_med": c["piece_w_med"],
                        "w_med": c["w_med"],
                        "boundaries": c["boundaries"],
                        "n_white_cuts": c["n_white_cuts"]})
    # ---- T5: rule-shred eye (Round 26 track-gate, (a)) ----
    # A run of abutting pieces whose union is a horizontal rule: the
    # segmenter cut one rule into pieces (R25 fuzzy track: p01/p2
    # rules shredded into 5). Text runs never qualify (union is a
    # text line ~1x med_h tall); a single unshredded rule is not a run.
    t5_list = ruleshred_candidates(gray, seg)
    for c in t5_list:
        reasons.append({"test": "T5-rule-shred", "box": c["box"],
                        "n_pieces": c["n_pieces"],
                        "piece_boxes": c["piece_boxes"],
                        "h_med": c["h_med"], "w_med": c["w_med"],
                        "dom_cc_frac": c["dom_cc_frac"]})
    verdict = "REFUSE" if reasons else "ALLOW"
    details = {"verdict": verdict, "sig_y": sig_y, "sig_y_v4": sig_y_v4, "img_h": h,
               "logo_rect": list(logo_rect) if logo_rect is not None else None,
               "n_words": len(words),
               "n_raw_clusters": n_raw,
               "t1_worst": [{"outside_frac": t[0], "extension_px": t[1],
                             "core_box": t[4], "word_idx": t[3],
                             "word_box": t[5]} for t in worst[:5]],
               "t1_flags": len(t1_kept), "t1_flags_raw": t1_flags_raw0,
               "t3_flags": len(t3_list), "t3_list": t3_list,
               "t4_flags": len(t4_list), "t4_list": t4_list,
               "t5_flags": len(t5_list), "t5_list": t5_list,
               "t1_seal_suppressed": len(t1_flags) - len(t1_kept),
               "t1_band_suppressed": len(t1_band_suppressed),
               "t1_band_suppressed_list": t1_band_suppressed,
               "t2_flags": len(t2_flags),
               "seal_boxes": seal_boxes,
               "reasons": reasons}
    return verdict, details


def calibrate(img, seg):
    """Measure the T1 outside-frac distribution (for threshold setting)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    words = seg["words"]
    lab, stats = core_ccs(gray)
    assign, _ = _assign_cores_min(lab, stats, words)
    fr = []
    for i, wi in assign.items():
        if wi < 0:
            continue
        x, y, cw, ch, area = (int(v) for v in stats[i])
        if cw > 120 or ch > 80:
            continue  # same word-size guard as T1
        if cw > 60 or area > 600:
            continue  # same letter-core shape guard as T1
        b = words[wi]["box"]
        x0, y0 = max(0, b[0] - 2), max(0, b[1] - 2)
        x1, y1 = min(w, b[2] + 2), min(h, b[3] + 2)
        core_mask = (lab[y:y + ch, x:x + cw] == i)
        total = int(core_mask.sum())
        if total == 0 or total < 100:
            continue  # same >=100px guard as T1
        ix0, iy0 = max(x, x0), max(y, y0)
        ix1, iy1 = min(x + cw, x1), min(y + ch, y1)
        inside = 0
        if ix1 > ix0 and iy1 > iy0:
            inside = int((lab[iy0:iy1, ix0:ix1] == i).sum())
        fr.append(1.0 - inside / total)
    fr = np.array(sorted(fr))
    return {"n_cores": len(fr),
            "frac_gt_0": int((fr > 0).sum()),
            "frac_gt_0.05": int((fr > 0.05).sum()),
            "frac_gt_0.25": int((fr > 0.25).sum()),
            "max_frac": round(float(fr.max()), 4) if len(fr) else 0.0,
            "p99": round(float(fr[int(0.99 * (len(fr) - 1))]), 4) if len(fr) else 0.0}


def ambiguous_band_cores(img, seg):
    """Inventory of ambiguous (-2) cores on one page (for the -2 rule check).

    Returns a list of {"box": [x, y, w, h], "area": int, "rule_shaped":
    bool, "band": bool} where "band" is True when cw > BAND_CORE_MIN_W
    (the rule would exclude this core from the mask). Also returns the
    mask-pixel contribution of all -2 cores (with vs without the rule).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    words = seg["words"]
    lab, stats = core_ccs(gray)
    assign, _amb = assign_cores(lab, stats, words)
    cores = []
    for i, wi in assign.items():
        if wi != -2:
            continue
        x, y, cw, ch, area = (int(v) for v in stats[i])
        cores.append({"box": [x, y, cw, ch], "area": area,
                      "rule_shaped": bool(is_rule_shaped(cw, ch, area)),
                      "band": bool(cw > BAND_CORE_MIN_W)})
    return cores


def mask_px_with_without_band(img, seg):
    """Mask px of full_page_mask() with the -2 band rule ON vs OFF.

    The OFF number is measured by rebuilding the mask with band cores
    included (same construction as full_page_mask, rule_exclusion=True).
    Returns (with_rule_px, without_rule_px, n_band_cores)."""
    _m_on, info_on = full_page_mask(img, seg, rule_exclusion=True)
    cores = ambiguous_band_cores(img, seg)
    # OFF = ON + the band cores' dilated ink (approximation-free: rebuild).
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    words = seg["words"]
    sig_y = detect_sig_y(gray, h)
    lab, stats = core_ccs(gray)
    assign, _amb = assign_cores(lab, stats, words)
    ink = (gray < INK_THR)
    all_cores = np.zeros((h, w), dtype=np.uint8)
    for i, wi in assign.items():
        if wi == -1:
            continue
        x, y, cw, ch, area = stats[i]
        if is_rule_shaped(cw, ch, area):
            continue
        m = (lab[y:y + ch, x:x + cw] == i).astype(np.uint8) * 255
        all_cores[y:y + ch, x:x + cw] = np.maximum(all_cores[y:y + ch, x:x + cw], m)
    ker = np.ones((3, 3), np.uint8)
    mask_off = (cv2.dilate(all_cores, ker, iterations=1) > 0) & ink
    mask_off = mask_off.astype(np.uint8) * 255
    _logo_off, _ = detect_logo_rect(gray)
    if _logo_off is not None:
        mask_off[_logo_off[1]:_logo_off[3], _logo_off[0]:_logo_off[2]] = 0
    mask_off[sig_y:h, :] = 0
    n_band = sum(1 for c in cores if c["band"])
    return info_on["mask_px"], int((mask_off > 0).sum()), n_band

def main():
    cmd, img_path, seg_path = sys.argv[1], sys.argv[2], sys.argv[3]
    img = cv2.imread(img_path)
    seg = json.load(open(seg_path))
    if cmd == "gate":
        verdict, details = gate(img, seg)
        print(json.dumps(details, indent=1))
        print("VERDICT:", verdict)
    elif cmd == "mask":
        m_off, i_off = full_page_mask(img, seg, rule_exclusion=False)
        m_on, i_on = full_page_mask(img, seg, rule_exclusion=True)
        print(json.dumps({"mask_px_no_exclusion": i_off["mask_px"],
                          "mask_px_with_exclusion": i_on["mask_px"],
                          "reduction_px": i_off["mask_px"] - i_on["mask_px"],
                          "reduction_pct": round(100 * (1 - i_on["mask_px"] / i_off["mask_px"]), 2),
                          "rule_cores_excluded": i_on["rule_cores_excluded"],
                          "sig_y": i_on["sig_y"],
                          "ambiguous_cores": i_on["ambiguous_cores"]}, indent=1))
    elif cmd == "calibrate":
        print(json.dumps(calibrate(img, seg), indent=1))
    else:
        print("usage: gate|mask|calibrate IMG SEG")
        sys.exit(2)


if __name__ == "__main__":
    main()
