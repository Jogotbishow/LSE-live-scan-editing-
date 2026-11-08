"""Segmentation-completeness gate (R17) — a DOCUMENTED QUALITY CHECK.

Ported from the GRAVORA prototype (scan-paper/improve/round17/track-b/
gate_ccmask.py). No OCR. The gate must guarantee NO silently-erased
seg-missed word: it REFUSEs (never erases) when it finds word-like ink
the seg does not cover, and only ALLOWs when the page is complete.

Two independent tests (either one REFUSEs):
  T1 core-outside: every core CC assigned to a word must lie (nearly)
     inside that word's box. Flag: outside_frac > 0.50 AND extension
     > 6 px beyond the box. (T1 threshold 0.50 is UNCHANGED — see
     DECISIONS.md. Do NOT promote this gate to a ship-gate.)
  T2 word-like uncovered cluster: R16 miss-hunt clustering verbatim,
     then word-like filters + logo / signature / rule exclusions.

DECISION (reversible, 2026-11-08 — see DECISIONS.md, "-2 band rule"):
full_page_mask() excludes band-shaped -2 cores (cw > 120 px) from the
mask — the same rule as ccmask.full_page_clean(). May's dotted title
band (449 px, ~14.5k mask px/page) is a highlight, not a word.
"""
import json

import cv2
import numpy as np

from .ccmask import INK_THR, assign_cores, core_ccs, detect_sig_y

CORE_OUT_FRAC = 0.50   # fraction of a core's pixels outside its word box
CORE_OUT_EXT = 6       # px the core must extend beyond the box edge
LOGO = (150, 120, 510, 450)  # same as inpaint.py v4 / R16 (300 DPI)

# -2 band rule (DECISIONS.md): band-shaped ambiguous core, not a word.
BAND_CORE_MIN_W = 120

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
    mask[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]] = 0
    mask[sig_y:h, :] = 0
    return mask, {"mask_px": int((mask > 0).sum()), "sig_y": int(sig_y),
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
    for t in t1_flags[:10]:
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
        if x0 >= LOGO[0] and y0 >= LOGO[1] and x1 <= LOGO[2] and y1 <= LOGO[3]:
            continue  # logo rect: mask zeroes it
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
        t2_flags.append(c)
    for c in t2_flags:
        reasons.append({"test": "T2-uncovered-wordlike", "box": c["box"],
                        "n_cc": c["n_cc"], "area": c["area"],
                        "med_cc_h": c["med_cc_h"],
                        "med_cc_area": c["med_cc_area"]})
    verdict = "REFUSE" if reasons else "ALLOW"
    details = {"verdict": verdict, "sig_y": sig_y, "sig_y_v4": sig_y_v4, "img_h": h,
               "n_words": len(words),
               "n_raw_clusters": n_raw,
               "t1_worst": [{"outside_frac": t[0], "extension_px": t[1],
                             "core_box": t[4], "word_idx": t[3],
                             "word_box": t[5]} for t in worst[:5]],
               "t1_flags": len(t1_flags), "t2_flags": len(t2_flags),
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
    mask_off[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]] = 0
    mask_off[sig_y:h, :] = 0
    n_band = sum(1 for c in cores if c["band"])
    return info_on["mask_px"], int((mask_off > 0).sum()), n_band


if __name__ == "__main__":
    import sys
    cmd, img_path, seg_path = sys.argv[1], sys.argv[2], sys.argv[3]
    img = cv2.imread(img_path)
    with open(seg_path) as _f:
        seg = json.load(_f)
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
