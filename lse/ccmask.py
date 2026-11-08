"""Connected-component masks (R15/R16) — the core-ink layer of LSE.

Ported from the GRAVORA prototype (scan-paper/improve/round15/track-c/
inpaint_ccmask.py and round16/track-c/inpaint_ccmask2.py). No OCR.

- INK_THR (210): a pixel darker than this is ink.
- CORE_THR (140): dark "cores" — at Otsu the E-ce label/value glyphs fuse
  into spanning blobs; at <140 only 5 still span. Cores are assigned to
  the word whose box holds most of their pixels; a core split across two
  words' boxes is AMBIGUOUS (-2) and is split at ysplit (R16 fix: the
  midpoint of the two words' own boxes, not the line median).
- full_page_clean() builds the build-time clean: union of dilated cores
  n ink, with rule-shaped cores excluded and logo + signature row kept.

DECISION (reversible, 2026-11-08 — see DECISIONS.md, "-2 band rule"):
band-shaped -2 cores (cw > 120 px) are EXCLUDED from the mask in
full_page_clean() and in gate.full_page_mask(). Evidence (R18): May's
dotted title band is 449 px wide, ~14.5k mask px/page — a highlight, not
a word; fused-letter -2 cores are <= 78 px; bands are >= 307 px; 120 sits
cleanly in the 78 -> 307 gap.
"""
import cv2
import numpy as np


INK_THR = 210
CORE_THR = 140

# -2 band rule (DECISIONS.md): a band-shaped ambiguous core is a
# highlight/rule, not a word. 120 px sits in the measured 78 -> 307 gap.
BAND_CORE_MIN_W = 120

LOGO = (150, 120, 510, 450)  # same as inpaint.py v4 (300 DPI)
TELEA_R = 6  # Telea inpaint radius (v4, 300 DPI)

def core_ccs(gray):
    """Dark-core CCs (grey < CORE_THR). Returns (labels, stats)."""
    _, bw = cv2.threshold(gray, CORE_THR, 255, cv2.THRESH_BINARY_INV)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bw, connectivity=8)
    return lab, stats


def assign_cores(lab, stats, words):
    """Assign each core CC to a word index (or -1). Returns (assign, ambiguous).
    ambiguous: list of (cc, counts, stats-row, ysplit) where the core's pixels
    are split across two words' boxes — genuinely fused. ysplit is the
    midpoint of the two words' glyph-band overlap: (median y1 of the upper
    word's line + lower word's box y0) // 2. Pixels above ysplit belong to
    the upper word, below to the lower word."""
    assign = {}
    ambiguous = []
    # median y1 per line (for the ysplit of fused cores)
    from collections import defaultdict
    line_y1 = defaultdict(list)
    for wd in words:
        if "line" in wd:
            line_y1[wd["line"]].append(wd["box"][3])
    med_y1 = {k: float(np.median(v)) for k, v in line_y1.items()}
    for i in range(1, len(stats)):
        x, y, cw, ch, area = stats[i]
        if area < 4:
            continue
        m = (lab[y:y + ch, x:x + cw] == i)
        counts = []
        for wi, wd in enumerate(words):
            bx0, by0, bx1, by1 = wd["box"]
            ox0, oy0 = max(x, bx0), max(y, by0)
            ox1, oy1 = min(x + cw, bx1), min(y + ch, by1)
            if ox1 <= ox0 or oy1 <= oy0:
                counts.append(0)
                continue
            sub = m[oy0 - y:oy1 - y, ox0 - x:ox1 - x]
            counts.append(int(sub.sum()))
        best = int(np.argmax(counts)) if counts else -1
        if not counts or counts[best] == 0:
            assign[i] = -1
            continue
        srt = sorted(counts, reverse=True)
        if len(srt) > 1 and srt[1] >= 0.25 * srt[0] and srt[1] > 0:
            # fused: split by y. Upper/lower = the two words by box y0.
            top2 = sorted(range(len(counts)), key=lambda k: -counts[k])[:2]
            up, lo = sorted(top2, key=lambda k: words[k]["box"][1])
            up_y1 = med_y1.get(words[up].get("line"), float(words[up]["box"][3]))
            ysplit = int((up_y1 + words[lo]["box"][1]) // 2)
            ambiguous.append((i, [int(c) for c in counts], stats[i].tolist(),
                              up, lo, ysplit))
            assign[i] = -2  # marker: split, handled in build_mask_cc
        else:
            assign[i] = best
    return assign, ambiguous


def assign_cores_fixed(lab, stats, words):
    """R15 assign_cores with ONE correction (this module only; the R15 file
    is frozen). R15's ysplit used the median y1 of the upper word's LINE:
    line 41 mixes two stacked rows (small words y1~1442 + E-ce labels
    y1~1464-1475), so the median (~1451) lands ABOVE fused cores whose
    tops are y1457+, making above==below==full core; contested-removal
    then deletes the core from BOTH reference masks (R_other=0, vacuous
    100% for the 'and'xBANGLADESH pair — measured, see RESULTS.md).
    Fix: ysplit = (upper WORD's own box y1 + lower WORD's box y0)//2,
    i.e. the midpoint of the two words' own glyph-band overlap, which is
    what R15's docstring describes. Plus a degenerate guard: a core that
    does not straddle ysplit is assigned whole by majority, never split.
    Returns (assign, ambiguous) in R15's format."""
    from collections import defaultdict
    assign = {}
    ambiguous = []
    for i in range(1, len(stats)):
        x, y, cw, ch, area = stats[i]
        if area < 4:
            continue
        m = (lab[y:y + ch, x:x + cw] == i)
        counts = []
        for wi, wd in enumerate(words):
            bx0, by0, bx1, by1 = wd["box"]
            ox0, oy0 = max(x, bx0), max(y, by0)
            ox1, oy1 = min(x + cw, bx1), min(y + ch, by1)
            if ox1 <= ox0 or oy1 <= oy0:
                counts.append(0)
                continue
            sub = m[oy0 - y:oy1 - y, ox0 - x:ox1 - x]
            counts.append(int(sub.sum()))
        best = int(np.argmax(counts)) if counts else -1
        if not counts or counts[best] == 0:
            assign[i] = -1
            continue
        srt = sorted(counts, reverse=True)
        if len(srt) > 1 and srt[1] >= 0.25 * srt[0] and srt[1] > 0:
            top2 = sorted(range(len(counts)), key=lambda k: -counts[k])[:2]
            up, lo = sorted(top2, key=lambda k: words[k]["box"][1])
            ysplit = int((words[up]["box"][3] + words[lo]["box"][1]) // 2)
            if ysplit <= y or ysplit >= y + ch:
                # core does not straddle the split: whole-core majority
                assign[i] = best
                continue
            ambiguous.append((i, [int(c) for c in counts], stats[i].tolist(),
                              up, lo, ysplit))
            assign[i] = -2
        else:
            assign[i] = best
    return assign, ambiguous


def split_core_halves(m, y, ysplit):
    """Split a core mask at ysplit: (above, below), both possibly empty.
    Correct at the edges (R15's code returned the FULL core for both
    halves when ysplit <= core top)."""
    above = m.copy()
    below = m.copy()
    if ysplit <= y:
        above[:, :] = 0
    elif ysplit >= y + m.shape[0]:
        below[:, :] = 0
    else:
        above[ysplit - y:, :] = 0
        below[:ysplit - y, :] = 0
    return above, below


def detect_sig_y(gray, h):
    """Same rule as inpaint.py v4: tall handwriting strokes in bottom 30%."""
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
    tall = [t for t in tall if t[1] > 0.7 * h and t[3] > 2.2 * med_h and t[2] < 300]
    return min(t[1] for t in tall) if len(tall) >= 2 else h


def full_page_clean(img, seg, passes=1):
    """Build-time candidate clean. Returns (clean_bgr, info)."""
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
        # -2 BAND RULE, SURGICAL (DECISIONS.md): a band-shaped
        # ambiguous (-2) core is a highlight/rule, not a word — exclude
        # it from the mask. BUT the core is often FUSED with word ink
        # (May: the dotted title band is one CC with the title
        # letters), so the exclusion is surgical: keep the part INSIDE
        # word boxes (those pixels are letters), drop the part outside
        # (the highlight dots). Whole-core exclusion would un-erase
        # the title words. (Same block in gate.full_page_mask.)
        # Fused-letter -2 cores are <= 78 px wide; bands are >= 307 px.
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
        # RULE EXCLUSION (measured R16): long rule CCs overlap word boxes
        # and get assigned to words; the naive union then erases the whole
        # table grid (277k px on Aug p2). Rules are long-thin, or big
        # sparse networks (the grid: bbox 2217x2134, fill 3.3%). Letter
        # CCs are <60px with fill >=0.25. Excluded cores are left for
        # pass 2, which only erases residual ink INSIDE word boxes.
        fill = area / max(1, cw * ch)
        if ((cw >= 150 and ch <= 10) or (ch >= 150 and cw <= 10) or
                (max(cw, ch) >= 150 and fill < 0.20)):
            n_rule_excluded += 1
            continue
        m = (lab[y:y + ch, x:x + cw] == i).astype(np.uint8) * 255
        cores[y:y + ch, x:x + cw] = np.maximum(cores[y:y + ch, x:x + cw], m)
    ker = np.ones((3, 3), np.uint8)
    mask = (cv2.dilate(cores, ker, iterations=1) > 0) & ink
    mask = mask.astype(np.uint8) * 255
    # v4 exclusions: logo + signature row never touched
    mask[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]] = 0
    mask[sig_y:h, :] = 0
    clean = cv2.inpaint(img, mask, TELEA_R, cv2.INPAINT_TELEA)
    info = {"mask_px": int((mask > 0).sum()), "sig_y": int(sig_y),
            "ambiguous_cores": len(ambiguous),
            "rule_cores_excluded": n_rule_excluded}
    if passes >= 2:
        g1 = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY)
        in_box = np.zeros((h, w), dtype=bool)
        for wd in words:
            x0, y0, x1, y1 = wd["box"]
            in_box[y0:y1, x0:x1] = True
        in_box[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]] = False
        in_box[sig_y:h, :] = False
        m2 = ((g1 < INK_THR) & in_box).astype(np.uint8) * 255
        m2 = cv2.dilate(m2, np.ones((3, 3), np.uint8), iterations=1)
        m2[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]] = 0
        m2[sig_y:h, :] = 0
        clean = cv2.inpaint(clean, m2, TELEA_R, cv2.INPAINT_TELEA)
        info["pass2_mask_px"] = int((m2 > 0).sum())
    return clean, info
