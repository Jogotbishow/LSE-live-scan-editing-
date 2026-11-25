"""Glyph retouch — the Photoshop layer of glyph harvest.

When a character NEVER appears on the page, harvest cannot supply
it (there is no ink to copy — e.g. lowercase 'x' on the Raviraj
page, needed for "2 max"). Retouch is the fallback: take the CLOSEST
font's glyph and rework it, like a retoucher in Photoshop, until it
looks like the document's own letters — then place it.

Every adjustment is MEASURED from the document's own harvested
glyphs, never guessed:
- width: the document/font width factor — the median, over every
  character the document and the font share, of (document glyph
  width / font glyph width at the same cap height). A missing
  character's target width is the font's width for it times that
  factor. It is an estimate anchored in 36 measured ratios, and it
  is reported as such.
- height: the document's x-height (median height of its harvested
  lowercase glyphs) for x-height letters, its cap height for caps.
- weight: the document's stem width (mode of the ink-run lengths
  in the middle band of a straight-stem harvested glyph). The
  retouched glyph is eroded or dilated at 2x supersampling until
  its stem matches, then downsampled.
- spacing: the document's own median gap.

A retouched glyph is NEVER presented as a harvested one: the
library marks it retouched with its source font, and compose()
records which letters of a string were retouched. If the eye-check
says a retouched letter does not belong, it is visible in the
record, not hidden.
"""

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


def measure_stem(bitmap):
    """Stroke width of a glyph bitmap: the mode of the horizontal
    ink-run lengths in the middle third of the glyph. For a straight
    stem ('l', 'H', 'N') the mode is the stem; for a diagonal ('x')
    it is the stroke width. Returns px (float) or None."""
    h, w = bitmap.shape
    if h < 6 or w < 3:
        return None
    runs = []
    for y in range(h // 3, (2 * h) // 3):
        row = bitmap[y]
        in_run = 0
        for v in row:
            if v:
                in_run += 1
            elif in_run:
                runs.append(in_run)
                in_run = 0
        if in_run:
            runs.append(in_run)
    if not runs:
        return None
    vals, counts = np.unique(runs, return_counts=True)
    return float(vals[int(np.argmax(counts))])


def _cap_height_fs(font_path, target_cap_h, supersample=2):
    """Font size (px) at which 'H' renders with cap height
    target_cap_h * supersample. Binary search on getbbox('H')."""
    lo, hi = 10, 400
    for _ in range(14):
        mid = (lo + hi) // 2
        f = ImageFont.truetype(font_path, mid)
        bb = f.getbbox("H")
        if bb[3] - bb[1] < target_cap_h * supersample:
            lo = mid
        else:
            hi = mid
    return lo


def render_font_glyph(font_path, char, cap_h_px, supersample=2):
    """Render one character from a font at the document's cap height
    (supersampled). Returns a grayscale PIL image (white bg, black
    ink) cropped tight to the ink."""
    fs = _cap_height_fs(font_path, cap_h_px, supersample)
    f = ImageFont.truetype(font_path, fs)
    img = Image.new("L", (600 * supersample, 300 * supersample), 255)
    ImageDraw.Draw(img).text((10, 10), char, font=f, fill=0)
    a = np.array(img) < 150
    ys, xs = np.where(a)
    if len(xs) == 0:
        return None, None
    crop = img.crop((int(xs.min()), int(ys.min()),
                     int(xs.max()) + 1, int(ys.max()) + 1))
    return crop, {"fs_px": fs, "cap_h_px": cap_h_px}


def width_factor(library, font_path, cap_h_px, like=None):
    """Median document/font width ratio over the characters the
    library and the font share (measured at the same cap height).
    ``like`` restricts the anchor to the target's case class
    (a lowercase 'a' is anchored on the document's lowercase
    letters, not on its caps — the classes have different width
    factors). The anchor for every retouched width."""
    ratios = []
    for ch in sorted(library.glyphs):
        if ch == " ":
            continue
        if like is not None:
            if like.islower() and not ch.islower():
                continue
            if like.isupper() and not ch.isupper():
                continue
            if like.isdigit() and not ch.isdigit():
                continue
        doc_w = library.glyphs[ch][0]["w"]
        img, _ = render_font_glyph(font_path, ch, cap_h_px, supersample=1)
        if img is None:
            continue
        ratios.append(doc_w / img.width)
    if not ratios:
        return None, []
    return float(np.median(ratios)), ratios


def retouch_glyph(font_path, char, target_w_px, target_h_px,
                  target_stem_px, cap_h_px, supersample=2):
    """Rework one font glyph toward the document's profile.

    1. Render at 2x the document's cap height.
    2. Scale horizontally to the target width, vertically to the
       target height (both LANCZOS on the grayscale image).
    3. Erode or dilate at 2x until the stem matches the target
       (1 iteration = ~1 px at 1x), then downsample to 1x.
    Returns (bitmap bool array, report). The bitmap is the retouched
    glyph at 1x, cropped tight."""
    img, _info = render_font_glyph(font_path, char, cap_h_px,
                                   supersample=supersample)
    if img is None:
        raise ValueError(f"font {font_path} has no glyph for {char!r}")
    # Targets are 1x px; the working image is supersampled, so scale
    # against supersampled targets (a 1x target against a 2x image
    # would halve the glyph twice — Raviraj proof, first run).
    scale_x = (target_w_px * supersample) / img.width
    scale_y = (target_h_px * supersample) / img.height
    w2 = max(2, int(round(img.width * scale_x)))
    h2 = max(2, int(round(img.height * scale_y)))
    img2 = img.resize((w2, h2), Image.LANCZOS)
    a2 = (np.array(img2) < 150).astype(np.uint8)
    stem2 = measure_stem(a2.astype(bool))
    target_stem2 = target_stem_px * supersample
    # Morph toward the target stem, keeping the BEST state seen:
    # measure_stem is a mode over run lengths, and on a diagonal
    # ('x') one dilate too many merges the strokes into a blob
    # whose mode run jumps far past the target (fin10: target 5.5,
    # two dilates, achieved stem 9.0). So after every step, keep the
    # state closest to the target and stop as soon as a step moves
    # away from it — never trust the last measurement alone.
    iters = 0
    if stem2 is not None and target_stem2 is not None:
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        best_a2 = a2.copy()
        best_err = abs(stem2 - target_stem2)
        while iters < 6:
            if stem2 > target_stem2 + 0.5:
                cand = cv2.erode(a2, kernel, iterations=1)
            elif stem2 < target_stem2 - 0.5:
                cand = cv2.dilate(a2, kernel, iterations=1)
            else:
                break
            cand_stem = measure_stem(cand.astype(bool))
            if cand_stem is None:
                break
            cand_err = abs(cand_stem - target_stem2)
            iters += 1
            if cand_err < best_err:
                best_a2, best_err = cand.copy(), cand_err
                a2, stem2 = cand, cand_stem
            else:
                break
        a2 = best_a2
        stem2 = measure_stem(a2.astype(bool))
    # Downsample to 1x: grayscale area average, threshold at 128.
    gray2 = np.where(a2 > 0, 0, 255).astype(np.uint8)
    small = Image.fromarray(gray2).resize(
        (max(1, w2 // supersample), max(1, h2 // supersample)),
        Image.LANCZOS)
    bitmap = np.array(small) < 128
    # Trim empty borders.
    ys, xs = np.where(bitmap)
    if len(xs) == 0:
        raise ValueError(f"retouch of {char!r} came out empty")
    bitmap = bitmap[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    achieved_stem = measure_stem(bitmap)
    report = {
        "char": char, "source_font": font_path,
        "target_w_px": target_w_px, "target_h_px": target_h_px,
        "target_stem_px": target_stem_px,
        "achieved_w_px": int(bitmap.shape[1]),
        "achieved_h_px": int(bitmap.shape[0]),
        "achieved_stem_px": achieved_stem,
        "morph_iters": iters,
        "scale_x": round(scale_x, 3), "scale_y": round(scale_y, 3),
    }
    return bitmap, report


def retouch_into_library(library, font_path, chars, cap_h_px=None,
                         x_height_px=None, stem_px=None, bold=False):
    """Retouch missing characters from a font into the library.

    Targets are measured from the library itself: cap height from
    its cap glyphs, x-height from its lowercase glyphs, stem from
    its straight-stem glyphs, width factor from the shared
    characters. Returns (reports, still_missing)."""
    if cap_h_px is None:
        cap_h_px = library.cap_height()
    if x_height_px is None:
        hs = [g["h"] for ch, vs in library.glyphs.items()
              for g in vs if ch.islower() and ch not in "ijl"]
        x_height_px = float(np.median(hs)) if hs else cap_h_px * 0.5
    if stem_px is None:
        stems = []
        for ch in ("l", "N", "U", "H", "I"):
            for v in library.glyphs.get(ch, []):
                # Same weight as the retouch: a bold invoice 'N' is
                # 7 px where a regular table 'N' is 5 px, and mixing
                # them moves the target (fin10 measured 5.5 for a
                # regular 'x' that way).
                if v.get("bold", False) != bold:
                    continue
                s = measure_stem(v["bitmap"])
                if s:
                    stems.append(s)
        stem_px = float(np.median(stems)) if stems else None
    factor, _ratios = width_factor(library, font_path, cap_h_px)
    if factor is None:
        raise ValueError("no shared characters to anchor the width factor")
    reports = []
    still_missing = []
    for ch in chars:
        if ch in library.glyphs:
            continue
        img, _ = render_font_glyph(font_path, ch, cap_h_px, supersample=1)
        if img is None:
            still_missing.append(ch)
            continue
        is_cap = ch.isupper() or ch.isdigit()
        target_h = cap_h_px if is_cap else x_height_px
        # Anchor the width on the target's own case class.
        class_factor, _ = width_factor(library, font_path, cap_h_px,
                                       like=ch)
        use_factor = class_factor if class_factor is not None else factor
        target_w = img.width * use_factor
        try:
            bitmap, rep = retouch_glyph(
                font_path, ch, target_w, target_h, stem_px, cap_h_px)
        except ValueError:
            still_missing.append(ch)
            continue
        h, w = bitmap.shape
        rec = {"char": ch, "bitmap": bitmap, "x0": 0,
               "top_rel": -h, "bottom_rel": 0, "w": w, "h": h,
               "gap_after": library.median_gap(),
               "gap_after_dot": library.median_gap(),
               "advance": w + library.median_gap(),
               "bold": bold, "retouched": True,
               "source_font": font_path}
        library.glyphs.setdefault(ch, []).append(rec)
        rep["width_factor"] = round(use_factor, 3)
        reports.append(rep)
    return reports, still_missing
