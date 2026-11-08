#!/usr/bin/env python3
"""Deskew — Live-Scan Round 2 step 5a.

First pipeline step: estimate a page's skew angle and correct it BEFORE
segmentation, so a crooked scan cannot silently produce wrong word boxes.

Method (classical, no ML, no OCR):
  1. Otsu-binarize, keep the ink mask.
  2. Projection-profile search: for each candidate angle in [-5, +5] deg
     (0.25 deg steps), rotate the mask and score = variance of the row ink
     profile. Correctly deskewed text concentrates ink into few rows, so
     the variance peaks at the true angle.
  3. Cross-check with a Hough transform on Canny edges (median angle of
     near-horizontal segments), reported but NOT used to pick the angle —
     the projection peak is the decision, Hough is the sanity check.

Correction policy (in segment.py): rotate only if |angle| >= 0.15 deg,
otherwise the image is passed through untouched (no resampling, no
pixel change). A deskewed page is written to a new file; the original
scan is never overwritten.

Usage:
  venv/bin/python improve/round2/deskew.py --image pages/aug-p1-1.png
  venv/bin/python improve/round2/deskew.py --test   # real pages + skewed copies
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(BASE, "improve", "round2")


def estimate_angle(gray, lo=-5.0, hi=5.0, step=0.25):
    """Return (correction_angle_deg, score_curve, hough_angle_deg_or_None).

    The returned angle is the CORRECTION to apply: rotating the image by
    this angle (cv2.getRotationMatrix2D, positive = counter-clockwise)
    maximises the row-profile variance, i.e. it undoes the page skew.
    Verified on artificially skewed copies (see deskew-test.json):
    true skew +1.0 deg -> correction -0.75..-1.0; -1.5 -> +1.5..+1.75;
    +3.0 -> -2.75..-3.0. Residual error <= one grid step (0.25 deg).
    A fine pass (0.1 deg) refines the coarse peak, and parabolic
    interpolation gives the sub-step peak.
    """
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ink = (bw > 0).astype(np.float32)
    h, w = ink.shape
    # restrict to the text area (exclude the outer border rows/cols a little)
    y0, y1 = int(0.05 * h), int(0.95 * h)
    ink_c = ink[y0:y1, :]

    def profile_var(a):
        m = cv2.getRotationMatrix2D((w / 2, (y1 - y0) / 2), a, 1.0)
        rot = cv2.warpAffine(ink_c, m, (w, y1 - y0),
                             flags=cv2.INTER_NEAREST, borderValue=0)
        return float(rot.sum(axis=1).var())

    curve = []
    a = lo
    while a <= hi + 1e-9:
        curve.append((round(a, 2), round(profile_var(a), 1)))
        a += step
    coarse = max(curve, key=lambda t: t[1])[0]
    # fine pass +-0.3 deg around the coarse peak, 0.1 deg steps
    fine = [(round(coarse + d, 2), round(profile_var(coarse + d), 1))
            for d in (-0.2, -0.1, 0.0, 0.1, 0.2)]
    curve.extend(fine)
    # parabolic interpolation on the fine pass
    xs = [f[0] for f in fine]
    ys = [f[1] for f in fine]
    i = int(np.argmax(ys))
    best_a = xs[i]
    if 0 < i < len(xs) - 1:
        y0_, y1_, y2_ = ys[i - 1], ys[i], ys[i + 1]
        denom = (y0_ - 2 * y1_ + y2_)
        if denom != 0:
            best_a = xs[i] + 0.1 * 0.5 * (y0_ - y2_) / denom
    best_a = round(float(best_a), 2)
    score0 = profile_var(0.0)
    score_best = profile_var(best_a)
    # Hough cross-check: median angle of near-horizontal line segments.
    edges = cv2.Canny((gray).astype(np.uint8), 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=200,
                            minLineLength=150, maxLineGap=10)
    hough = None
    if lines is not None:
        segs = lines.reshape(-1, 4)  # OpenCV 5 returns (N,4); older (N,1,4)
        angs = []
        for l in segs:
            x0, y0_, x1, y1_ = l
            dx, dy = x1 - x0, y1_ - y0_
            if abs(dx) < 50:
                continue
            ang = float(np.degrees(np.arctan2(dy, dx)))
            if abs(ang) < 10:
                angs.append(ang)
        if len(angs) >= 5:
            hough = round(float(np.median(angs)), 2)
    return best_a, curve, hough, round(score0, 1), round(score_best, 1)


def correct(img, angle):
    """Rotate by +angle (the correction angle from estimate_angle)."""
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def make_skewed(img, angle, out_path):
    """Artificially skew a page by +angle degrees (for the test)."""
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    sk = cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(out_path, sk)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image")
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    if args.test:
        import subprocess
        results = {}
        for name, path in (("aug", os.path.join(BASE, "pages/aug-p1-1.png")),
                           ("may", os.path.join(BASE, "pages/may-p1-1.png"))):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            ang, curve, hough, s0, sb = estimate_angle(img)
            gain = (sb - s0) / s0 * 100 if s0 else 0
            print(f"{name} real page: correction {ang:+.2f} deg "
                  f"(Hough {hough}; score@0={s0:.0f}, score@best={sb:.0f}, "
                  f"gain {gain:+.2f}%)")
            results[name] = {"real": {"correction_deg": ang, "hough_deg": hough,
                                      "score_at_0": s0, "score_at_best": sb,
                                      "gain_pct": round(gain, 2)}}
            for true_deg in (1.0, -1.5, 3.0):
                sk_path = os.path.join(OUT, f"deskew-{name}-skew{true_deg:+.1f}.png")
                make_skewed(cv2.imread(path), true_deg, sk_path)
                sk = cv2.imread(sk_path, cv2.IMREAD_GRAYSCALE)
                est, _, hough2, s0b, sbb = estimate_angle(sk)
                # est is the CORRECTION: expected value is -true_deg
                err = est - (-true_deg)
                corr = correct(cv2.imread(sk_path), est)
                corr_path = os.path.join(
                    OUT, f"deskew-{name}-skew{true_deg:+.1f}-corrected.png")
                cv2.imwrite(corr_path, corr)
                resid, _, _, _, _ = estimate_angle(
                    cv2.imread(corr_path, cv2.IMREAD_GRAYSCALE))
                # segmentation on the corrected page vs the original counts
                seg_out = os.path.join(OUT, f"deskew-{name}-skew{true_deg:+.1f}-seg.json")
                r = subprocess.run([sys.executable,
                                    os.path.join(BASE, "segment.py"),
                                    corr_path, seg_out],
                                   cwd=BASE, capture_output=True, text=True)
                n_words = None
                if r.returncode == 0:
                    n_words = len(json.load(open(seg_out))["words"])
                print(f"  skewed {true_deg:+.1f} deg -> correction {est:+.2f} deg "
                      f"(expect {-true_deg:+.1f}; error {err:+.2f} deg, Hough {hough2}); "
                      f"after correction residual {resid:+.2f} deg; "
                      f"seg words on corrected page: {n_words}")
                results[name][f"skew{true_deg:+.1f}"] = {
                    "true_deg": true_deg, "correction_deg": est,
                    "expected_correction_deg": -true_deg,
                    "error_deg": round(err, 2), "hough_deg": hough2,
                    "residual_after_correction_deg": resid,
                    "seg_words_after_correction": n_words}
        json.dump(results, open(os.path.join(OUT, "deskew-test.json"), "w"), indent=1)
        print("wrote improve/round2/deskew-test.json")
        return

    gray = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
    ang, curve, hough, s0, sb = estimate_angle(gray)
    print(f"correction angle: {ang:+.2f} deg (Hough cross-check: {hough})")
    print(f"score@0={s0:.0f} score@best={sb:.0f} gain={(sb-s0)/s0*100:+.2f}%")
    print("curve (angle, row-profile variance):", curve)


if __name__ == "__main__":
    main()
