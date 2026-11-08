"""Document DNA — build a render font from the document's own glyphs.

Ported from the GRAVORA prototype (scan-paper/improve/round2/dna-prod/
dna-build-prod.py, Round 2 step 9b+c). The tracer spike's measured
winner was VTRACER (IoU 0.955 vs potrace 0.950 vs img2bez 0.933,
smallest file, 0.4 s; vtracer is MIT OR Apache-2.0).

Inputs (produced by the glyph-extraction steps, see API.md):
  median_dir: directory of 8x median glyph PNGs, one per character,
    named ``dna-<ord:03d>-<char|sym>-8x.png`` (prototype convention).
  per_char: {char: {"trace_h": ..., "advance_units": ...,
    "bot_off_units": ...}} — measured glyph geometry, from the
    ``glyphs-weights-{dpi}.json`` of the extraction run.
  cap_trace_px: image px equal to the 700-unit cap height
    (36 at 300 DPI, 72 at 600 DPI).

Geometry: unitsPerEm 1000, regular cap height 700 units; bold cap height
is MEASURED (bold capitals are ~29 px vs 27 px regular at 300 DPI, so
~758 units) and reported in the build record — the live page sizes each
weight from its own measured cap ratio. SCALE = font units per 8x-median
px = 700 / (cap_trace_px * 8).

The built fonts are LOCAL rendering aids only — never distributed as
font files. The build is deterministic from the median glyphs; the
record reports glyph IoU vs its own medians, width/height error, file
size, outline points and mean segment length (staircase proxy).
"""
import json
import os
import re
import time

import cv2
import numpy as np
import vtracer

from ._tracer import build_ttf, fname, measure_font, parse_path, signed_area, split_contours


def trace_vtracer_for(median_dir, chars, scale):
    """vtracer cutout+polygon on the 8x median PNGs of one weight/DPI set.

    Same conversion as the prototype tracer spike (black paths only,
    bbox containment -> hole orientation). Returns {char: [contours]} in
    font units, y-up, y=0 at the glyph's bottom edge.
    """
    out = {}
    for ch in chars:
        fn = fname(ch)
        png = os.path.join(median_dir, fn + "-8x.png")
        im = cv2.imread(png, cv2.IMREAD_GRAYSCALE)
        if im is None:
            raise FileNotFoundError(png)
        H, W = im.shape
        rgba = np.dstack([im, im, im, np.full(im.shape, 255, np.uint8)])
        cfg = vtracer.Config(hierarchical="cutout", mode="polygon",
                             filter_speckle=4, binary_threshold=128)
        svg = vtracer.convert_pixels(rgba.tobytes(), W, H, cfg)
        paths = re.findall(r'<path d="([^"]+)" fill="(#[0-9A-Fa-f]+)"/>', svg)
        contours = []
        for d, fill in paths:
            if fill.upper() != "#000000":
                continue
            segs = parse_path(d)
            for contour in split_contours(segs):
                contours.append(contour)
        flipped = []
        for contour in contours:
            fc = []
            for kind, v in contour:
                if v is None:
                    fc.append((kind, None))
                elif kind == "C":
                    fc.append((kind, (v[0] * scale, (H - v[1]) * scale,
                                      v[2] * scale, (H - v[3]) * scale,
                                      v[4] * scale, (H - v[5]) * scale)))
                else:
                    fc.append((kind, (v[0] * scale, (H - v[1]) * scale)))
            flipped.append(fc)

        def bbox(c):
            xs, ys = [], []
            for kind, v in c:
                if kind in ("M", "L"):
                    xs.append(v[0]); ys.append(v[1])
                elif kind == "C":
                    xs += [v[0], v[2], v[4]]; ys += [v[1], v[3], v[5]]
            return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)

        boxes = [bbox(c) for c in flipped]
        oriented = []
        for i, c in enumerate(flipped):
            is_hole = any(j != i and boxes[j][0] <= boxes[i][0] and boxes[j][1] <= boxes[i][1]
                          and boxes[j][2] >= boxes[i][2] and boxes[j][3] >= boxes[i][3]
                          for j in range(len(flipped)))
            area = signed_area(c)
            want_neg = not is_hole
            if (area < 0) != want_neg and area != 0:
                if any(k == "C" for k, _ in c):
                    print(f"  WARNING {ch}: curved contour not reversed")
                else:
                    verts = [(k, v) for k, v in c if k in ("M", "L")]
                    c = [verts[0]] + [(k, v) for k, v in reversed(verts[1:])]
            oriented.append(c)
        out[ch] = oriented
    return out


def build_dna_font(median_dir, per_char, cap_trace_px, out_path,
                   family="PGCloneDNA", style="Regular", dpi=600):
    """Build one Document DNA font (one weight, one DPI).

    ``per_char`` is the {char: geometry} dict for this weight (from
    ``glyphs-weights-{dpi}.json``). Returns the build record dict
    (glyphs, file size, cap height in font units + ratio, IoU scores,
    width/height errors, outline points, mean segment length).
    """
    chars = sorted(per_char.keys())
    scale = 700.0 / (cap_trace_px * 8)
    t0 = time.time()
    traces = trace_vtracer_for(median_dir, chars, scale)
    n_points = build_ttf(traces, out_path, family, style, chars, per_char)
    caps = [per_char[c]["trace_h"] * 8 * scale for c in chars
            if c.isupper() and per_char[c]["trace_h"] >= 30]
    cap_units = float(np.median(caps)) if caps else 700.0
    m = measure_font(out_path, chars, per_char, median_dir, scale)
    seg_lens = []
    for ch in chars:
        for contour in traces[ch]:
            pts = []
            for kind, v in contour:
                if kind in ("M", "L"):
                    pts.append(v)
                elif kind == "C":
                    pts.append((v[4], v[5]))
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                seg_lens.append(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
    rec = {"dpi": dpi, "weight": style.lower(),
           "glyphs": len(chars), "chars": "".join(chars),
           "ttf": os.path.basename(out_path),
           "ttf_bytes": os.path.getsize(out_path),
           "outline_points": n_points,
           "mean_segment_len_units": round(float(np.mean(seg_lens)), 1),
           "median_segment_len_units": round(float(np.median(seg_lens)), 1),
           "cap_height_units": round(cap_units, 1),
           "cap_ratio": round(cap_units / 1000, 3),
           "build_s": round(time.time() - t0, 1),
           "iou_digits": m["iou_digits"], "iou_letters": m["iou_letters"],
           "iou_all": m["iou_all"],
           "width_err_mean_pct": m["width_err_mean_pct"],
           "height_err_mean_pct": m["height_err_mean_pct"],
           "per_char": m["per_char"]}
    print(f"{style}-{dpi}: {len(chars)} glyphs, {rec['ttf_bytes']}B, "
          f"cap {rec['cap_height_units']}u (ratio {rec['cap_ratio']}), "
          f"IoU dig {m['iou_digits']} let {m['iou_letters']} all {m['iou_all']}, "
          f"width_err {m['width_err_mean_pct']}%, height_err {m['height_err_mean_pct']}%, "
          f"mean seg {rec['mean_segment_len_units']}u, {rec['build_s']}s")
    return rec


def build_dna_fonts(weights_json_path, median_root, out_dir,
                    family="PGCloneDNA", dpis=(300, 600)):
    """Build all DNA fonts for a weights file.

    ``weights_json_path``: ``glyphs-weights-{dpi}.json`` (one file per
    DPI, each with ``per_char_regular`` / ``per_char_bold`` and
    ``cap_trace_px``). ``median_root`` holds ``median-{weight}-{dpi}``
    directories. Writes ``dna-clone-{weight}-{dpi}.ttf`` + a build
    record JSON into ``out_dir``. Returns the record dict.
    """
    os.makedirs(out_dir, exist_ok=True)
    results = {}
    for dpi in dpis:
        path = weights_json_path.format(dpi=dpi) if "{dpi}" in weights_json_path else weights_json_path
        g = json.load(open(path))
        for weight in ("regular", "bold"):
            per_char = g[f"per_char_{weight}"]
            median_dir = os.path.join(median_root, f"median-{weight}-{dpi}")
            out_ttf = os.path.join(out_dir, f"dna-clone-{weight}-{dpi}.ttf")
            results[f"{weight}-{dpi}"] = build_dna_font(
                median_dir, per_char, g["cap_trace_px"], out_ttf,
                family=family, style="Regular" if weight == "regular" else "Bold",
                dpi=dpi)
    json.dump(results, open(os.path.join(out_dir, "dna-prod-build.json"), "w"), indent=1)
    print("wrote dna-prod-build.json")
    return results
