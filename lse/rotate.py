"""Rotation detection (Round 4 Track C) — combined detector.

Ported from the GRAVORA prototype (scan-paper/rotate_detect.py). No OCR
text is read — OSD uses shape statistics only.

  1. AXIS by projection-profile line_score (pure OpenCV): upright text
     has sharp horizontal line structure; a 90-degree error smears it.
  2. FLIP within the axis by Tesseract OSD (``tesseract --psm 0``).
  3. LOW-CONFIDENCE OVERRIDE: if the axis is 0/180 AND OSD confidence
     < 1.0 AND flip3 finds >= 10 genuine horizontal lines with
     |score| >= 0.15, trust flip3's flip verdict instead.

Measured accuracy on the prototype set: 34/35 (the one miss, Raviraj
p05, is wrong under OSD, flip2, flip3 and bottom-strip OSD alike).

NOTE: Tesseract is OPTIONAL here. When it is not installed, osd()
returns (None, None) and detect() falls back to projection + flip3
only (method "osd-missing->assume-upright" / flip3 verdicts). The
package therefore still detects 90/270 rotations without Tesseract,
but the 0-vs-180 flip then rests on flip3 alone.
"""
import json
import os
import re
import subprocess

import cv2

from ._rotate_flip3 import flip3
from ._rotate_proj import detect as proj_detect


def osd(path):
    """(orientation_degrees, confidence) from Tesseract OSD, or (None, None)
    when Tesseract is not installed (optional dependency)."""
    try:
        r = subprocess.run(["tesseract", path, "stdout", "--psm", "0"],
                           capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, OSError):
        return None, None
    out = r.stdout + r.stderr
    m = re.search(r"Orientation in degrees:\s*(\d+)", out)
    c = re.search(r"Orientation confidence:\s*([\d.]+)", out)
    return (int(m.group(1)) if m else None,
            float(c.group(1)) if c else None)


def detect(path, verbose=False):
    pr = proj_detect(path)
    sc = pr["scores"]
    axis_h = max(sc[0], sc[180]) >= max(sc[90], sc[270])  # True: 0/180 axis
    o, c = osd(path)
    evidence = {"proj_scores": {k: round(v, 1) for k, v in sc.items()},
                "axis": "0/180" if axis_h else "90/270",
                "osd_orient": o, "osd_conf": c}
    method = "osd"
    if axis_h:
        # flip within the 0/180 axis
        flip_upright = None
        if c is not None and c < 1.0:
            f, n, _ = flip3(path)
            evidence["flip3"] = {"score": round(f, 2), "n_lines": n}
            if n >= 10 and abs(f) >= 0.15:
                flip_upright = f > 0
                method = "osd-lowconf+flip3"
        if flip_upright is None:
            if o in (0, 180):
                flip_upright = (o == 0)
            elif o in (90, 270):
                evidence["warning"] = "OSD axis disagrees with projection; trusting projection axis, flip from flip3"
                f, n, _ = flip3(path)
                evidence["flip3"] = {"score": round(f, 2), "n_lines": n}
                flip_upright = f > 0 if n >= 10 else True
                method = "axis-mismatch+flip3"
            else:
                flip_upright = True
                method = "osd-missing->assume-upright"
        correction = 0 if flip_upright else 180
    else:
        # 90/270 axis: only OSD distinguishes the two directions
        if o in (90, 270):
            correction = (360 - o) % 360
        else:
            evidence["warning"] = "OSD axis disagrees with projection; trusting projection pick"
            correction = 90 if sc[90] >= sc[270] else 270
            method = "axis-mismatch+proj"
    evidence["method"] = method
    return correction, evidence


def apply_correction(img, correction):
    if correction == 0:
        return img
    if correction == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if correction == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if correction == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise ValueError(correction)


def detect_array(img):
    """detect() for an in-memory BGR image (writes a temp PNG for OSD)."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        cv2.imwrite(path, img)
        return detect(path)
    finally:
        os.unlink(path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4 and sys.argv[1] == "--apply":
        img = cv2.imread(sys.argv[2])
        corr, ev = detect(sys.argv[2])
        cv2.imwrite(sys.argv[3], apply_correction(img, corr))
        print(f"{sys.argv[2]} -> correction {corr} CW; evidence={json.dumps(ev)}")
        sys.exit(0)
    for p in sys.argv[1:]:
        corr, ev = detect(p)
        print(f"{os.path.basename(p):28s} correction={corr:3d} CW  {json.dumps(ev)}")
