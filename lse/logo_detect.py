#!/usr/bin/env python3
"""Round 19 Track-Logo — page-adaptive logo exclusion (replaces the fixed
LOGO rect (150,120,510,450) of segment.py v5-300 / gate_ccmask.py).

Measured basis (scan_seeds.py, scan2_out.txt, crops — all in this dir):
- PG letterhead: PREM GROUP emblem = 2 large CCs (~168x204, fill 0.28-0.44)
  at (232,217)-(436,423), caption "PREM GROUP" letters at y174-202 directly
  above it, thin frame rules at x~196 and x~467 spanning y143-455.
- Raviraj customs pages p22-p27: Indian emblem seal = 2 seed CCs
  (133x124 fill 0.51 + 195x87 fill 0.34) at (212,188)-(407,351), plus its
  outer ring CC (147x163, fill 0.09) reaching y156.
- Raviraj p01 (landscape consignment note): MATA wordmark = 6 seed CCs
  (letters ~112x107 + swoosh pieces 220x91 / 219x101), union
  (397,161)-(840,494); tagline "Nothing too far" starts x898, the
  "(Formerly known as..." line starts y~511 — both outside the rect.
- The other 18 of the 25 Raviraj pages have NO in-zone seed at all: their
  top-left holds real text (CITY, Corporate, consign, ORIGINAL, GO...),
  so the correct exclusion there is NONE.
- Other big graphics on the same pages (Raviraj RF chevron logo at
  x~1207 top-centre, GCC stamp at x~1349 y~603, IBA seal at x~1160 y~365,
  customs seal at x~2141 top-right) are OUTSIDE the letterhead logo zone
  and were never covered by the fixed rect; they are deliberately NOT
  touched here — their handling is unchanged.

Rule (300-DPI px, same scale as segment.py v5-300):
  Zone = top-left letterhead zone, seed bbox fully inside x<=1000, y<=600.
  Seed = CC with w>=70 and h>=70, area>=1500, w<=700, h<=700, fill>=0.15
  (excludes the hollow page-border frame, fill ~0.01-0.05, and title
  letters, which are <=~64px). Seeds cluster by gap<=80px.
  A cluster needs >=2 seeds (every true in-zone logo measured has 2-6;
  a lone big CC is left alone — safe direction: text is preserved).
  Then absorb, in order: (a) large CCs (w>=60, h>=60, area>=1000)
  overlapping the bbox+30 (the seal's low-fill outer ring); (b) rule CCs
  (w<=15 & h>=100, or h<=15 & w>=100) overlapping bbox+45 (PG frame
  rules); (c) a caption row: >=3 letter-like CCs (8<=w<=60, 10<=h<=60)
  with centres in the 80px band above the bbox and x within bbox+-20,
  sharing a y-band of 15px (PG "PREM GROUP"). Final pad 10px.
  No cluster -> None (no exclusion).

No OCR anywhere. Read-only on the image.
"""
import cv2
import numpy as np

ZONE_X1 = 1000
ZONE_Y1 = 600
SEED_MIN = 70
SEED_MIN_AREA = 1500
SEED_MAX = 700
SEED_MIN_FILL = 0.15
CLUSTER_GAP = 80
MIN_SEEDS = 2
ABSORB_LARGE_GAP = 30
ABSORB_RULE_GAP = 45
CAPTION_BAND = 80
PAD = 10


def _ccs(gray):
    otsu, bw = cv2.threshold(gray, 0, 255,
                             cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num, _lab, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    out = []
    for i in range(1, num):
        x, y, w, h, area = (int(v) for v in stats[i])
        out.append({"x": x, "y": y, "w": w, "h": h, "area": area,
                    "cx": float(cent[i][0]), "cy": float(cent[i][1])})
    return out


def _bbox(boxes):
    return (min(b["x"] for b in boxes), min(b["y"] for b in boxes),
            max(b["x"] + b["w"] for b in boxes),
            max(b["y"] + b["h"] for b in boxes))


def _overlaps(b, rect, gap):
    """True if CC b overlaps rect expanded by gap on all sides."""
    return not (b["x"] + b["w"] < rect[0] - gap or b["x"] > rect[2] + gap
                or b["y"] + b["h"] < rect[1] - gap or b["y"] > rect[3] + gap)


def detect_logo_rect(gray, verbose=False):
    """Return (x0, y0, x1, y1) exclusion rect, or None. Also returns info."""
    ccs = _ccs(gray)
    seeds = [c for c in ccs
             if c["w"] >= SEED_MIN and c["h"] >= SEED_MIN
             and c["area"] >= SEED_MIN_AREA
             and c["w"] <= SEED_MAX and c["h"] <= SEED_MAX
             and c["area"] / (c["w"] * c["h"]) >= SEED_MIN_FILL
             and c["x"] + c["w"] <= ZONE_X1 and c["y"] + c["h"] <= ZONE_Y1]
    if verbose:
        print(f"logo-detect: in-zone seeds={len(seeds)} "
              f"{[(s['x'], s['y'], s['w'], s['h']) for s in seeds]}")
    if len(seeds) < MIN_SEEDS:
        return None, {"n_seeds": len(seeds), "clusters": 0}
    # cluster seeds by gap<=80 in both axes
    clusters = []
    for s in sorted(seeds, key=lambda c: (c["y"], c["x"])):
        placed = False
        for cl in clusters:
            for c in cl:
                gx = max(0, max(s["x"], c["x"]) - min(s["x"] + s["w"], c["x"] + c["w"]))
                gy = max(0, max(s["y"], c["y"]) - min(s["y"] + s["h"], c["y"] + c["h"]))
                if gx <= CLUSTER_GAP and gy <= CLUSTER_GAP:
                    cl.append(s)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            clusters.append([s])
    # keep the cluster with most seeds (ties -> largest area); require >=2
    clusters = [cl for cl in clusters if len(cl) >= MIN_SEEDS]
    if not clusters:
        return None, {"n_seeds": len(seeds), "clusters": 0}
    best = max(clusters, key=lambda cl: (len(cl), sum(c["area"] for c in cl)))
    base = _bbox(best)
    rect = base
    if verbose:
        print(f"logo-detect: cluster n={len(best)} bbox={base}")
    # Absorb steps are evaluated against the FIXED seed bbox (base), never
    # against the growing rect: the page-border frame is one huge CC that
    # overlaps everything, and a growing rect would swallow the whole page.
    # (a) absorb large CCs fully inside base+60 that overlap base+30
    # (the seal's low-fill outer ring, which is not a seed itself).
    for c in ccs:
        if c in best:
            continue
        if (c["w"] >= 60 and c["h"] >= 60 and c["area"] >= 1000
                and c["x"] >= base[0] - 60 and c["y"] >= base[1] - 60
                and c["x"] + c["w"] <= base[2] + 60
                and c["y"] + c["h"] <= base[3] + 60
                and _overlaps(c, base, ABSORB_LARGE_GAP)):
            best.append(c)
            rect = _bbox(best)
    # (b) absorb nearby rule CCs (PG frame rules): centre inside base+60
    # and overlapping base+45 (a page-wide rule's centre is far away).
    for c in ccs:
        if c in best:
            continue
        is_rule = ((c["w"] <= 15 and c["h"] >= 100)
                   or (c["h"] <= 15 and c["w"] >= 100))
        if (is_rule and base[0] - 60 <= c["cx"] <= base[2] + 60
                and base[1] - 60 <= c["cy"] <= base[3] + 60
                and _overlaps(c, base, ABSORB_RULE_GAP)):
            best.append(c)
            rect = _bbox(best)
    if verbose:
        print(f"logo-detect: after absorb large+rule bbox={rect}")
    # (c) absorb a caption row directly above the bbox
    cands = [c for c in ccs
             if c["area"] >= 14 and 8 <= c["w"] <= 60 and 10 <= c["h"] <= 60
             and rect[1] - CAPTION_BAND <= c["cy"] <= rect[1]
             and rect[0] - 20 <= c["cx"] <= rect[2] + 20]
    if len(cands) >= 3:
        cands.sort(key=lambda c: c["cy"])
        # largest group sharing a 15px y-band
        groups, cur = [], [cands[0]]
        for c in cands[1:]:
            if c["cy"] - cur[0]["cy"] <= 15:
                cur.append(c)
            else:
                groups.append(cur)
                cur = [c]
        groups.append(cur)
        grp = max(groups, key=len)
        if len(grp) >= 3:
            cap = _bbox(grp)
            rect = (min(rect[0], cap[0]), min(rect[1], cap[1]),
                    max(rect[2], cap[2]), max(rect[3], cap[3]))
            if verbose:
                print(f"logo-detect: caption row n={len(grp)} bbox={cap} -> {rect}")
    rect = (rect[0] - PAD, rect[1] - PAD, rect[2] + PAD, rect[3] + PAD)
    info = {"n_seeds": len(seeds), "clusters": len(clusters),
            "cluster_n": len(best), "rect": rect}
    if verbose:
        print(f"logo-detect: FINAL rect={rect}")
    return rect, info
