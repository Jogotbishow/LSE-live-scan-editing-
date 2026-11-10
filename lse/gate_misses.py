"""Round 17 Track B — Part 2: seg-completeness gate for full-page CC-mask.

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
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logo_detect import detect_logo_rect  # noqa: E402

import cv2
import numpy as np

BASE = "/home/hatch/workspace/gravora-review/live-paper-prototype/scan-paper/"
TRACKB = BASE + "improve/round17/track-b/"

_spec = importlib.util.spec_from_file_location(
    "ccmask2_r16", BASE + "improve/round16/track-c/inpaint_ccmask2.py")
_cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cc)

core_ccs = _cc.core_ccs
assign_cores = _cc.assign_cores
detect_sig_y = _cc.detect_sig_y
INK_THR = _cc.INK_THR
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
    assign, ambiguous = assign_cores(lab, stats, words)
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
    verdict = "REFUSE" if reasons else "ALLOW"
    details = {"verdict": verdict, "sig_y": sig_y, "sig_y_v4": sig_y_v4, "img_h": h,
               "logo_rect": list(logo_rect) if logo_rect is not None else None,
               "n_words": len(words),
               "n_raw_clusters": n_raw,
               "t1_worst": [{"outside_frac": t[0], "extension_px": t[1],
                             "core_box": t[4], "word_idx": t[3],
                             "word_box": t[5]} for t in worst[:5]],
               "t1_flags": len(t1_kept), "t1_flags_raw": t1_flags_raw0,
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
    assign, _ = assign_cores(lab, stats, words)
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
