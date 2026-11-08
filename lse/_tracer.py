"""SVG path parsing + TTF assembly for Document DNA fonts.

Ported from the GRAVORA prototype (scan-paper/improve/round2/dna-prod/
tracer-spike.py). The prototype used module globals (CHARS, PER_CHAR,
MED, SCALE, UPM); this package version takes them as explicit
parameters so one process can build several fonts. Behaviour is
unchanged: parse_path handles the M/L/C/Z subset vtracer emits,
build_ttf assembles a TrueType font with fontTools (quadratic outlines,
cap height 700 units by construction), measure_font scores the built
font against its own median bitmaps (IoU / width / height error).
"""
import os
import re

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def parse_path(d):
    """Parse SVG path data (absolute/relative M/L/C/Z, implicit repeats)
    into [(kind, coords)] with coords absolute. Same parser as
    dna-build-font.py (potrace dialect); img2bez emits the same subset."""
    tokens = re.findall(r"[MLCZmlcz]|-?\d+(?:\.\d+)?", d)
    segs, i, cur, start = [], 0, (0.0, 0.0), None
    last_cmd = None
    while i < len(tokens):
        tok = tokens[i]
        if re.fullmatch(r"[MLCZmlcz]", tok):
            cmd = tok
            i += 1
        elif re.fullmatch(r"-?\d+(?:\.\d+)?", tok):
            if last_cmd is None:
                raise ValueError(f"number before any command in {d[:80]}")
            cmd = "L" if last_cmd in "Mm" else last_cmd
        else:
            raise ValueError(f"unexpected token {tok!r} in path {d[:80]}")
        if cmd in "Mm":
            x, y = float(tokens[i]), float(tokens[i + 1]); i += 2
            if cmd == "m":
                x, y = cur[0] + x, cur[1] + y
            segs.append(("M", (x, y))); cur = (x, y); start = (x, y)
            last_cmd = cmd
        elif cmd in "Ll":
            x, y = float(tokens[i]), float(tokens[i + 1]); i += 2
            if cmd == "l":
                x, y = cur[0] + x, cur[1] + y
            segs.append(("L", (x, y))); cur = (x, y)
            last_cmd = cmd
        elif cmd in "Cc":
            pts = [float(tokens[j]) for j in range(i, i + 6)]; i += 6
            if cmd == "c":
                pts = [pts[0] + cur[0], pts[1] + cur[1],
                       pts[2] + cur[0], pts[3] + cur[1],
                       pts[4] + cur[0], pts[5] + cur[1]]
            segs.append(("C", tuple(pts))); cur = (pts[4], pts[5])
            last_cmd = cmd
        elif cmd in "Zz":
            segs.append(("Z", None))
            if start is not None:
                cur = start
            last_cmd = cmd
        else:
            raise ValueError(f"unexpected token {cmd!r} in path {d[:80]}")
    return segs


def split_contours(segs):
    """Split a flat segment list into contours (lists of segments)."""
    contours, cur = [], []
    for kind, v in segs:
        if kind == "M" and cur:
            contours.append(cur)
            cur = []
        cur.append((kind, v))
    if cur:
        contours.append(cur)
    return contours


def signed_area(contour):
    """Signed area of a contour's polygon (on-curve points only, y-up
    coords: positive = counter-clockwise)."""
    pts = []
    for kind, v in contour:
        if kind in ("M", "L"):
            pts.append(v)
        elif kind == "C":
            pts.append((v[4], v[5]))
    if len(pts) < 3:
        return 0.0
    a = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        a += x1 * y2 - x2 * y1
    return a / 2.0


def build_ttf(traces, out_path, family, style, chars, per_char, upm=1000):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.misc.transform import Transform
    glyph_order = [".notdef", "space"] + [f"u{ord(c):04X}" for c in chars]
    cmap = {ord(c): f"u{ord(c):04X}" for c in chars}
    cmap[0x20] = "space"
    fb = FontBuilder(upm)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    glyphs, metrics = {}, {}
    pen = TTGlyphPen(None)
    glyphs[".notdef"] = pen.glyph()
    metrics[".notdef"] = (500, 0)
    pen = TTGlyphPen(None)
    glyphs["space"] = pen.glyph()
    metrics["space"] = (250, 0)
    n_points = 0
    for ch in chars:
        info = per_char[ch]
        pen = TTGlyphPen(None)
        bot_units = info.get("bot_off_units", 0)
        tr = Transform(1, 0, 0, 1, 0, bot_units)
        cpen = Cu2QuPen(TransformPen(pen, tr), max_err=1.0, reverse_direction=True)
        for contour in traces[ch]:
            start = None
            for kind, v in contour:
                if kind == "M":
                    if start is not None:
                        cpen.closePath()
                    cpen.moveTo(v); start = v
                elif kind == "L":
                    cpen.lineTo(v)
                elif kind == "C":
                    cpen.curveTo(v[0:2], v[2:4], v[4:6])
                elif kind == "Z":
                    cpen.closePath(); start = None
            if start is not None:
                cpen.closePath()
            n_points += len(contour)
        glyphs[f"u{ord(ch):04X}"] = pen.glyph()
        metrics[f"u{ord(ch):04X}"] = (info["advance_units"], 0)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-250)
    fb.setupNameTable({"familyName": family, "styleName": style,
                       "uniqueFontIdentifier": f"{family}-{style}-tracer-spike",
                       "fullName": f"{family} {style}",
                       "version": "Version 1.0",
                       "psName": f"{family}-{style}"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-250, usWinAscent=800, usWinDescent=250)
    fb.font["OS/2"].sCapHeight = 700  # production fix (step 9): cap height
    # is 700 units by construction; expose it so browsers/tools read it.
    fb.setupPost()
    fb.save(out_path)
    return n_points


def norm_height_mask(mask, h=24):
    """Resize a binary mask to fixed height h (keep aspect), NEAREST."""
    hh, ww = mask.shape
    nw = max(1, round(ww * h / hh))
    return cv2.resize(mask, (nw, h), interpolation=cv2.INTER_NEAREST)




def fname(ch):
    """Median-glyph file stem for one character (prototype convention)."""
    return f"dna-{ord(ch):03d}-{ch if ch.isalnum() else 'sym'}"


def measure_font(ttf_path, chars, per_char, median_dir, scale):
    """Per-glyph IoU / width error / height error vs the median bitmaps."""
    font200 = ImageFont.truetype(ttf_path, 200)
    font100 = ImageFont.truetype(ttf_path, 100)
    # NOTE: the input ``per_char`` (median measurements) must NOT be
    # shadowed here — an earlier port wrote ``per_char, heights = {}, []``
    # and then looked up per_char[ch] in the empty dict (KeyError).
    results, heights = {}, []
    for ch in chars:
        info = per_char[ch]
        med = cv2.imread(os.path.join(median_dir, fname(ch) + ".png"), cv2.IMREAD_GRAYSCALE)
        med_ink = (med < 128).astype(np.uint8)
        med_n = norm_height_mask(med_ink, 24)
        # render at size 200, ink bbox, normalise to height 24
        im = Image.new("L", (400, 400), 255)
        d = ImageDraw.Draw(im)
        d.text((50, 50), ch, font=font200, fill=0)
        arr = np.array(im)
        ys, xs = np.where(arr < 128)
        if len(xs) == 0:
            results[ch] = {"iou": 0.0, "width_err_pct": 100.0, "height_err_pct": 100.0}
            continue
        ren = (arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1] < 128).astype(np.uint8)
        ren_n = norm_height_mask(ren, 24)
        w = max(med_n.shape[1], ren_n.shape[1])
        A = np.zeros((24, w), np.uint8); B = np.zeros((24, w), np.uint8)
        A[:, (w - med_n.shape[1]) // 2:(w - med_n.shape[1]) // 2 + med_n.shape[1]] = med_n
        B[:, (w - ren_n.shape[1]) // 2:(w - ren_n.shape[1]) // 2 + ren_n.shape[1]] = ren_n
        inter = int(np.logical_and(A, B).sum()); union = int(np.logical_or(A, B).sum())
        iou = inter / union if union else 0.0
        werr = abs(ren_n.shape[1] - med_n.shape[1]) / med_n.shape[1] * 100
        # height check at size 100: expected ink height px
        im2 = Image.new("L", (300, 300), 255)
        d2 = ImageDraw.Draw(im2)
        d2.text((50, 50), ch, font=font100, fill=0)
        arr2 = np.array(im2)
        ys2, xs2 = np.where(arr2 < 128)
        ren_h = (ys2.max() - ys2.min() + 1) if len(xs2) else 0
        exp_h = info["trace_h"] * 8 * scale * (100 / 1000)
        herr = abs(ren_h - exp_h) / exp_h * 100 if exp_h else 100.0
        heights.append(herr)
        results[ch] = {"iou": round(float(iou), 3),
                       "width_err_pct": round(float(werr), 1),
                       "height_err_pct": round(float(herr), 1)}
    digits = [results[c]["iou"] for c in chars if c.isdigit()]
    letters = [results[c]["iou"] for c in chars if c.isalpha()]
    werrs = [results[c]["width_err_pct"] for c in chars]
    return {"per_char": results,
            "iou_digits": round(float(np.mean(digits)), 3),
            "iou_letters": round(float(np.mean(letters)), 3),
            "iou_all": round(float(np.mean([results[c]["iou"] for c in chars])), 3),
            "width_err_mean_pct": round(float(np.mean(werrs)), 1),
            "height_err_mean_pct": round(float(np.mean(heights)), 1)}
