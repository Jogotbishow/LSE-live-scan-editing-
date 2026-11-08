"""Rotation detection, method B: projection-profile (pure OpenCV, no OCR).
For each candidate upright rotation r in {0,90,180,270} (degrees CW to apply
to the STORED image to make it upright), score the rotated image:
  line_score = var(row_ink) / mean(row_ink)  -- upright text has sharp
    horizontal line structure (peaks at text lines, empty gaps); a 90-degree
    error smears every row across many vertical text columns -> low variance.
  flip_score = mean over detected line bands of ink(top-half)/ink(bottom-half)
    -- Latin print is top-heavy inside a line (x-height + ascenders dense,
    descenders sparse below the baseline); a 180-degree error flips it.
    Computed on the 0/180 pair only (the 90/270 pair is decided by line_score).
Usage: rotate_proj.py <img...>  -> per file, scores per candidate + pick.
"""
import sys, os
import cv2
import numpy as np

def prep(img):
    h, w = img.shape[:2]
    s = 800 / max(w, h)
    small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return (bw > 0).astype(np.float32)

def line_score(bw):
    row = bw.sum(axis=1)
    m = row.mean()
    return float(row.var() / m) if m > 0 else 0.0

def flip_score(bw):
    """Top-heaviness of text-line bands. Returns ratio top/bottom ink."""
    row = bw.sum(axis=1)
    thr = 0.15 * row.max()
    bands, cur = [], None
    for y, v in enumerate(row):
        if v > thr:
            cur = [y, y] if cur is None else [cur[0], y]
        else:
            if cur is not None:
                bands.append(tuple(cur)); cur = None
    if cur is not None:
        bands.append(tuple(cur))
    ratios = []
    for (y0, y1) in bands:
        hgt = y1 - y0 + 1
        if hgt < 4 or hgt > 40:
            continue
        band = bw[y0:y1 + 1, :]
        mid = hgt // 2
        top = band[:mid, :].sum()
        bot = band[mid:, :].sum()
        if top + bot > 20:
            ratios.append(top / max(1.0, bot))
    if not ratios:
        return 1.0, 0
    return float(np.median(ratios)), len(ratios)

def detect(path):
    img = cv2.imread(path)
    rots = {0: img, 90: cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE),
            180: cv2.rotate(img, cv2.ROTATE_180),
            270: cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)}
    scores = {}
    for r, im in rots.items():
        bw = prep(im)
        scores[r] = line_score(bw)
    # axis: 0/180 pair vs 90/270 pair by line_score
    axis0 = max(scores[0], scores[180])
    axis90 = max(scores[90], scores[270])
    if axis0 >= axis90:
        cand = 0 if scores[0] >= scores[180] else 180
        # flip check on the two candidates
        f0, n0 = flip_score(prep(rots[0]))
        f180, n180 = flip_score(prep(rots[180]))
        flip_pick = 0 if f0 >= f180 else 180
        return {"scores": scores, "pick": cand, "pick_by": "line",
                "flip0": round(f0, 2), "flip180": round(f180, 2),
                "flip_pick": flip_pick, "n_bands": n0}
    else:
        cand = 90 if scores[90] >= scores[270] else 270
        f90, _ = flip_score(prep(rots[90]))
        f270, _ = flip_score(prep(rots[270]))
        flip_pick = 90 if f90 >= f270 else 270
        return {"scores": scores, "pick": cand, "pick_by": "line",
                "flip90": round(f90, 2), "flip270": round(f270, 2),
                "flip_pick": flip_pick, "n_bands": 0}

if __name__ == "__main__":
    for p in sys.argv[1:]:
        d = detect(p)
        sc = {k: round(v, 1) for k, v in d["scores"].items()}
        extra = {k: v for k, v in d.items() if k not in ("scores", "pick", "pick_by")}
        print(f"{os.path.basename(p):28s} scores={sc} pick={d['pick']} ({d['pick_by']}) {extra}")
