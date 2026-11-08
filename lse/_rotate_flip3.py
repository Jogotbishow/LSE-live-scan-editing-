"""flip3: baseline-alignment discriminator, hardened.
vs flip2: (a) line must be a genuine horizontal text line — x-span >= 150px
and y-span <= 2.5*med_h (excludes vertical margin text and diagonal
watermarks, which poisoned flip2 on the customs pages p22-p27);
(b) score per line = modal-bottom count minus modal-top count, but only
lines with >= 8 components count, and the page score is the SUM over lines
of the per-line difference normalised by line size (so one huge table
cannot drown the page).
Usage: rotate_flip3.py <img...>
"""
import sys, os
import cv2
import numpy as np
from collections import Counter

def flip3(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    s = 1200 / max(w, h)
    small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num, lab, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    comps = []
    for i in range(1, num):
        x, y, ww, hh, area = (int(v) for v in stats[i])
        if 6 <= hh <= 45 and 3 <= ww <= 60 and area >= 8:
            comps.append((x, y, ww, hh))
    if not comps:
        return 0, 0, 0
    med_h = sorted(c[3] for c in comps)[len(comps) // 2]
    comps.sort(key=lambda c: c[1] + c[3] / 2)
    lines = []
    for c in comps:
        cy = c[1] + c[3] / 2
        placed = False
        for ln in lines:
            if abs(cy - ln["cy"]) <= max(4, 0.6 * med_h):
                ln["items"].append(c)
                ln["cy"] = sum(i[1] + i[3] / 2 for i in ln["items"]) / len(ln["items"])
                placed = True
                break
        if not placed:
            lines.append({"cy": cy, "items": [c]})
    def best(counter):
        return max((sum(counter.get(v + d, 0) for d in (-1, 0, 1))
                    for v in counter), default=0)
    score = 0.0
    n_lines = 0
    for ln in lines:
        items = ln["items"]
        if len(items) < 8:
            continue
        xs = [i[0] for i in items]; xe = [i[0] + i[2] for i in items]
        ys = [i[1] for i in items]; ye = [i[1] + i[3] for i in items]
        span_x, span_y = max(xe) - min(xs), max(ye) - min(ys)
        if span_x < 150 or span_y > 2.5 * med_h:
            continue
        n_lines += 1
        bots = Counter(i[1] + i[3] for i in items)
        tops = Counter(i[1] for i in items)
        score += (best(bots) - best(tops)) / len(items)
    return score, n_lines, med_h

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s, n, mh = flip3(p)
        print(f"{os.path.basename(p):28s} flip3 score={s:+6.2f} over {n} horizontal lines (med_h={mh}) -> {'UPRIGHT' if s > 0 else 'FLIPPED-180' if s < 0 else '?'}")
