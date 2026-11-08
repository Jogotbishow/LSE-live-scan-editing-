"""Remove printed text from a scan page (inpaint v4, Round 2).

Ported from the GRAVORA prototype (scan-paper/inpaint.py). For each word
box, mask dark pixels inside the box and Telea-inpaint; the title
highlight bar is masked wholesale and its underline re-drawn crisp;
per-region paper grain (Grain v2) is restored after Telea. Logo area and
the detected handwritten signature row are never touched.

Package version: the proven script body is wrapped in clean_page(); the
algorithm is unchanged. No OCR anywhere in this module.
"""
import json

import cv2
import numpy as np


def clean_page(img, words, grain=True):
    """Erase every word in ``words`` from ``img`` (BGR numpy array).

    ``words`` is a list of {"box": [x0, y0, x1, y1]} dicts (or a seg dict
    with a "words" key). Returns (clean_bgr, info) where info reports
    removed/skipped counts, masked pixels, the detected title bar /
    underline rows and sig_y. The input image is never modified.
    """
    if isinstance(words, dict):
        words = words["words"]
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # regions to never touch: logo (top-left) and the handwritten signature row (never OCR'd).
    # The signature row is DETECTED per page (same rule as segment.py v2: handwriting
    # strokes in the bottom 30% are far taller than print, h > 2.2x median char height;
    # if >= 2 exist, sig_y = the top of the highest one, else no exclusion).
    # The old hardcoded y=2030 clipped the printed note line on the May page (REPORT-MAY.md §4 bug 2).
    LOGO = (150, 120, 510, 450)         # x0,y0,x1,y1 at 300 DPI (x1.5)

    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    num, _labels, stats, _cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    _letter_h = []
    _tall = []
    for _i in range(1, num):
        _x, _y, _ww, _hh, _area = stats[_i]
        if _area < 14:  # 6 x 2.25
            continue
        if (_ww > 375 and _hh < 9) or (_hh > 180 and _ww < 9):  # x1.5
            continue
        if _ww > 900 or _hh > 180:  # x1.5
            continue
        _letter_h.append(_hh)
        _tall.append((_x, _y, _ww, _hh))
    _med_h = sorted(_letter_h)[len(_letter_h) // 2] if _letter_h else 18
    _tall = [t for t in _tall if t[1] > 0.7 * h and t[3] > 2.2 * _med_h and t[2] < 300]  # x1.5 (missed at first: Aug p2 sig_y fell to h)
    sig_y = min(t[1] for t in _tall) if len(_tall) >= 2 else h
    print(f"signature row detected: sig_y={sig_y} (from {len(_tall)} tall strokes)")
    SIGROW = (0, sig_y, w, h)            # handwritten signatures + dates

    def overlaps(a, b):
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


    # ---- v3: title highlight bar + underline detection (pixel-only, no OCR) ----
    def _colrun(g, y0, y1, thr=240):
        colmean = g[y0:y1 + 1, :].astype(float).mean(axis=0)
        cols = np.where(colmean < thr)[0]
        best, cs = (0, 0), None
        for c in cols:
            if cs is None:
                cs = p = c
            elif c == p + 1:
                p = c
            else:
                if p - cs > best[1] - best[0]:
                    best = (cs, p)
                cs = p = c
        if cs is not None and p - cs > best[1] - best[0]:
            best = (cs, p)
        return best, best[1] - best[0] + 1

    def detect_bar(g):
        """Title highlight bar: uniform halftone rectangle. Row profile r[y] =
        fraction of centre-band pixels with grey < 230 stays > 0.20 for 25+
        consecutive rows (text lines break into ~20-row runs); the column run
        of mean grey < 240 over the run must be one contiguous run >= 250 px
        (dense table text gives >1000 px, header/logo ~135 px, body line ~207 px).
        Edges refined by walking while r > 0.10 (max 12 px)."""
        hh, ww = g.shape
        xlo, xhi = int(0.30 * ww), int(0.70 * ww)
        r = (g[:, xlo:xhi] < 230).mean(axis=1)
        r = np.convolve(r, np.ones(5) / 5.0, mode='same')  # 300-DPI FIX I1: smooth halftone screen
        top = int(0.40 * hh)
        runs, s = [], None
        for y in range(top):
            if r[y] > 0.20:
                if s is None:
                    s = y
            else:
                if s is not None:
                    runs.append((s, y - 1))
                    s = None
        if s is not None:
            runs.append((s, top - 1))
        for (a, b) in runs:
            if b - a + 1 < 32:  # 300-DPI FIX I3: May bars are 36-37 smoothed rows; col-run is the guard
                continue
            (_, _), cwd = _colrun(g, a, b, 240)
            if cwd < 375:  # 250 x 1.5
                continue
            y0 = a
            while y0 > 0 and y0 > a - 18 and r[y0 - 1] > 0.10:  # 12 x 1.5
                y0 -= 1
            y1 = b
            while y1 < hh - 1 and y1 < b + 18 and r[y1 + 1] > 0.10:  # 12 x 1.5
                y1 += 1
            (x0, x1), _ = _colrun(g, y0, y1, 245)
            return (int(x0), int(y0), int(x1), int(y1))
        return None

    def _longest_run(row_dark):
        best = cur = 0
        for v in row_dark:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        return best

    def detect_underline(g, bar):
        """Solid rule inside/just below the bar. Core rows: longest contiguous
        dark (<96) run >= 0.60 x bar width (letter rows max ~0.07). Expanded to
        adjacent rows with dark fraction >= 0.50 (the rule's soft edges).
        Returns (y0, y1) or None."""
        x0, y0, x1, y1 = bar
        bw = x1 - x0 + 1
        core = []
        for y in range(y0, min(y1 + 7, g.shape[0])):
            _row_dark = g[y, x0:x1 + 1] < 96
            if (_longest_run(_row_dark) >= 0.60 * bw or
                    (float(_row_dark.mean()) >= 0.90 and _longest_run(_row_dark) >= 0.30 * bw)):  # FIX I2
                core.append(y)
        if not core:
            return None
        lo, hi = min(core), max(core)
        while lo > y0 and float((g[lo - 1, x0:x1 + 1] < 96).mean()) >= 0.50:
            lo -= 1
        while hi < min(y1 + 6, g.shape[0] - 1) and float((g[hi + 1, x0:x1 + 1] < 96).mean()) >= 0.50:
            hi += 1
        return (lo, hi)

    bar = detect_bar(gray)
    underline = detect_underline(gray, bar) if bar else None
    print(f"title bar detected: {bar}")
    print(f"underline rows detected: {underline}")

    mask = np.zeros((h, w), dtype=np.uint8)
    removed, skipped = 0, 0
    for wd in words:
        x0, y0, x1, y1 = [int(v) for v in wd["box"]]
        x0 = max(0, x0 - 2); y0 = max(0, y0 - 2)
        x1 = min(w, x1 + 2); y1 = min(h, y1 + 2)
        if overlaps((x0, y0, x1, y1), LOGO) or overlaps((x0, y0, x1, y1), SIGROW):
            skipped += 1
            continue
        roi = gray[y0:y1, x0:x1]
        # ink pixels = text. Threshold 210 catches grey anti-aliased edges too (v1: 170 left ghosts)
        m = (roi < 210).astype(np.uint8) * 255
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], m)
        removed += 1

    # v3: the whole highlight bar is one mask element (not per-word boxes), so the
    # bar's dither cannot survive between words and the underline cannot sit on a
    # hole boundary. The bar contains only title words (already masked) + the
    # underline (re-drawn below); logo/signature/table lines are outside it.
    if bar is not None:
        bx0, by0, bx1, by1 = bar
        mask[by0:by1 + 1, bx0:bx1 + 1] = 255
        print(f"bar filled into mask: x {bx0}-{bx1}, y {by0}-{by1} "
              f"({(bx1-bx0+1)*(by1-by0+1)} px)")

    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)  # 3x3 x1.5 -> 5x5
    clean = cv2.inpaint(img, mask, 6, cv2.INPAINT_TELEA)  # radius 4 x 1.5

    # ---- v4 (Round 2, step 6a): Grain v2 — per-region paper grain re-add ----
    # Telea leaves patches too smooth (Round 1 C1: sigma_in 3.88 vs paper 7.54).
    # Grain v1 (one global sigma) created stains on grey areas. v2, measured in
    # improve/round2/grain2-spike.py on the same 5 crops: per-16px-tile sigma
    # from the tile's ring in the ORIGINAL (white-paper pixels > 200 only —
    # the first G2 run used (90, 210] too and text edges inflated sigma 2x,
    # C1 sigma_in 16.07, May sigma 8.87 on sigma-0 paper: FAILED, fixed);
    # top-up amount sqrt(paper^2 - result^2); grey tiles (ring median < 220)
    # and flat paper (sigma < 0.5, May) get NO grain; noise clipped to the
    # tile's paper [p1, p99]. Measured: C1 sigma_in 3.88 -> 6.28 (paper 7.54),
    # tile-match 5.43 -> 1.41, ghost still 0; C3 sigma 3.21 -> 3.89 (paper
    # 3.83); May C4/C5 byte-identical to Telea (no grain added). --no-grain
    # disables it (spike comparisons / fallback).
    def grain_v2(orig_bgr, result_bgr, mask, tile=24, ring=36, seed=7):  # tile/ring x1.5
        import numpy as _np
        _rng = _np.random.default_rng(seed)
        gray = cv2.cvtColor(orig_bgr, cv2.COLOR_BGR2GRAY)
        res = result_bgr.astype(_np.float32)
        h, w = gray.shape
        m = mask > 0
        for ty in range(0, h, tile):
            for tx in range(0, w, tile):
                th = min(tile, h - ty)
                tw = min(tile, w - tx)
                tmask = m[ty:ty + th, tx:tx + tw]
                if not tmask.any():
                    continue
                rx0, ry0 = max(0, tx - ring), max(0, ty - ring)
                rx1, ry1 = min(w, tx + tile + ring), min(h, ty + tile + ring)
                ring_g = gray[ry0:ry1, rx0:rx1].astype(_np.float32)
                ring_m = mask[ry0:ry1, rx0:rx1] == 0
                if not ring_m.any() or float(_np.median(ring_g[ring_m])) < 220:
                    continue  # grey area (e.g. highlight bar) -> no grain
                paper = ring_g[ring_m]
                paper = paper[paper > 200]
                if len(paper) < 20:
                    continue
                sig_paper = float(paper.std())
                if sig_paper < 0.5:
                    continue  # flat paper (May B&W, sigma 0) -> no grain
                res_gray_tile = cv2.cvtColor(
                    result_bgr[ty:ty + th, tx:tx + tw],
                    cv2.COLOR_BGR2GRAY).astype(_np.float32)
                sig_res = float(res_gray_tile[tmask].std()) if tmask.sum() > 5 else 0.0
                sig_add = float(_np.sqrt(max(0.0, sig_paper ** 2 - sig_res ** 2)))
                if sig_add < 0.5:
                    continue
                p1, p99 = float(_np.percentile(paper, 1)), float(_np.percentile(paper, 99))
                noise = _rng.normal(0, sig_add, (th, tw)).astype(_np.float32)
                sub = res[ty:ty + th, tx:tx + tw]
                add = _np.zeros((th, tw, 1), _np.float32)
                add[:, :, 0] = noise
                sub2 = sub + add * tmask[..., None]
                lo = _np.full((th, tw, 1), p1, _np.float32)
                hi = _np.full((th, tw, 1), p99, _np.float32)
                sub2 = _np.where(tmask[..., None] > 0, _np.clip(sub2, lo, hi), sub)
                res[ty:ty + th, tx:tx + tw] = sub2
        return _np.clip(res, 0, 255).astype(_np.uint8)

    if grain:
        clean = grain_v2(img, clean, mask)
        print("grain v2 applied (per-region sigma, seed 7)")
    else:
        print("grain v2 skipped (grain=False)")

    # v3: re-draw the underline as a crisp line. Only pixels that were dark
    # (<100) in the ORIGINAL and lie OUTSIDE every word box are set to the
    # underline ink colour (mean BGR of dark pixels on the core rows). Letter
    # bottoms (e.g. May row 417: all 156 dark px are inside title boxes) are
    # therefore never drawn back. Edge rows keep only their truly-dark fragments.
    if bar is not None and underline is not None:
        bx0, by0, bx1, by1 = bar
        uy0, uy1 = underline
        core_rows = [y for y in range(uy0, uy1 + 1)
                     if (_longest_run(gray[y, bx0:bx1 + 1] < 96) >= 0.60 * (bx1 - bx0 + 1) or
                         (float((gray[y, bx0:bx1 + 1] < 96).mean()) >= 0.90 and
                          _longest_run(gray[y, bx0:bx1 + 1] < 96) >= 0.30 * (bx1 - bx0 + 1)))]  # FIX I2b
        ink_px = []
        for y in core_rows:
            ink_px.append(img[y, bx0:bx1 + 1][gray[y, bx0:bx1 + 1] < 96])
        ink = np.concatenate(ink_px).mean(axis=0) if ink_px else np.array([0, 0, 0])
        ink = tuple(int(round(v)) for v in ink)  # BGR
        in_box = np.zeros((h, w), dtype=bool)
        for wd in words:
            x0, y0, x1, y1 = [int(v) for v in wd["box"]]
            in_box[y0:y1, x0:x1] = True
        n_drawn = 0
        for y in range(uy0, uy1 + 1):
            sel = (gray[y, bx0:bx1 + 1] < 100) & (~in_box[y, bx0:bx1 + 1])
            clean[y, bx0:bx1 + 1][sel] = ink
            n_drawn += int(sel.sum())
        print(f"underline re-drawn: rows {uy0}-{uy1} (core {core_rows}), "
              f"ink BGR {ink}, pixels set: {n_drawn}")

    info = {"removed": removed, "skipped_logo_signature": skipped,
            "masked_px": int((mask > 0).sum()),
            "masked_pct": round(100 * (mask > 0).sum() / (h * w), 2),
            "title_bar": bar, "underline_rows": underline,
            "sig_y": int(sig_y)}
    print(f"boxes removed: {removed}, skipped (logo/signature): {skipped}")
    print(f"masked pixels: {info['masked_px']} of {h*w} ({info['masked_pct']:.2f}%)")
    return clean, info

def clean_file(img_path, seg_path, out_path, grain=True):
    """Read image + seg JSON, write the cleaned image. CLI convenience."""
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(img_path)
    with open(seg_path) as f:
        seg = json.load(f)
    clean, info = clean_page(img, seg["words"], grain=grain)
    cv2.imwrite(out_path, clean)
    print(f"saved: {out_path}")
    return clean, info


if __name__ == "__main__":
    import sys
    _grain = "--no-grain" not in sys.argv
    _args = [a for a in sys.argv[1:] if a != "--no-grain"]
    clean_file(_args[0], _args[1], _args[2], grain=_grain)
