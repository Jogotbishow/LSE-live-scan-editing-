"""Font fingerprinting: measure a document's OWN letterforms and rank
candidate fonts by how closely they reproduce them.

Why this exists (2026-11-24, the user's PLNU catch): the transplant's
sizes measured 0% but the FONT DESIGN was wrong — Liberation Serif's
P/L/N/U/0 shapes are wider/rounder than the original's. Hand-guessing
cost three rounds (Liberation -> Noto Condensed -> Liberation -> Nimbus
Roman). This module MEASURES the answer instead: fingerprint the ink in
a probe box (cap height, x-height, stem width, slash height, ink width)
and rank every installed serif by the same measurements rendered at the
same cap height. The winner is the font whose letterforms match, not
just whose metrics match.

Rules the module follows (all learned the hard way tonight):
- Text size = CAP height from components, never ink-box height:
  slashes (and ascenders) inflate the box. The cap is the MEDIAN
  height of the tall components — slashes are few, so the median
  ignores them.
- Weight is verified by STEM width (median run on the cap-mid
  scanline) AND by ink width, never by eye.
- PIL probe widths are RELATIVE only: a probe can rank fonts against
  each other but never proves an absolute width against the original
  — the pipeline render is the truth. The ranking below is therefore
  a ranking, and the final proof is always the pipeline render.
- A font file is identified by its PATH; the original's font is
  usually Times New Roman (Excel/Windows) — if that file is ever in
  the font library, it must win the ranking on its own.
- HONEST LIMIT, found 2026-11-24 on the real Raviraj scan: the
  component fingerprint ALONE ranks the WRONG font on scans
  (P052/Noto beat Nimbus on the spec probe). Scan ink spreads (dot
  gain fattens ink_w ~7%) and letters touch (components merge, so
  x_h reads 0), while the PIL probe renders are unstretched and the
  pipeline stretches the text layer to the fit box (~+12% on the
  spec) — so probe widths and pipeline widths are different rulers.
  The overlay score (best-IoU of the rendered string against the
  scan's ink) is therefore the PRIMARY signal on scans; the
  fingerprint distance is secondary (it works on clean renders).
"""

from __future__ import annotations

import glob
import os
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover - cv2 is a hard dep of lse
    cv2 = None

from PIL import Image, ImageDraw, ImageFont

from .fonts import available_serif_candidates

# Weights for the distance: width and stem matter most (they are what
# the eye reads as "the same font"); slash height and x-height are
# secondary; cap is matched by construction so its weight is small.
WEIGHTS = {"cap_h": 1.0, "x_h": 1.0, "stem_w": 2.0, "slash_h": 1.0, "ink_w": 2.0}

# (display name, path) — discovery keeps only files that exist.
_KNOWN_SERIFS = [
    ("LiberationSerif-Regular", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"),
    ("LiberationSerif-Bold", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"),
    ("NimbusRoman-Regular", "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf"),
    ("NimbusRoman-Bold", "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf"),
    ("C059-Roman", "/usr/share/fonts/opentype/urw-base35/C059-Roman.otf"),
    ("C059-Bold", "/usr/share/fonts/opentype/urw-base35/C059-Bold.otf"),
    ("P052-Roman", "/usr/share/fonts/opentype/urw-base35/P052-Roman.otf"),
    ("P052-Bold", "/usr/share/fonts/opentype/urw-base35/P052-Bold.otf"),
    ("NotoSerif-Regular", "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"),
    ("NotoSerif-Bold", "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"),
    ("NotoSerif-Condensed", "/usr/share/fonts/truetype/noto/NotoSerif-Condensed.ttf"),
    ("NotoSerif-CondensedSemiBold", "/usr/share/fonts/truetype/noto/NotoSerif-CondensedSemiBold.ttf"),
    ("DejaVuSerif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    ("DejaVuSerif-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
]


def system_serif_candidates() -> List[Tuple[str, str]]:
    """Installed serif fonts this machine can actually render."""
    return [(n, p) for n, p in _KNOWN_SERIFS if os.path.exists(p)]


def candidates_from_dirs(dirs: Sequence[str]) -> List[Tuple[str, str]]:
    """Every .ttf/.otf in the given dirs (e.g. a Windows Fonts folder
    copied in, so the original's real font can enter the ranking)."""
    out = []
    for d in dirs:
        for ext in ("*.ttf", "*.otf"):
            for p in sorted(glob.glob(os.path.join(d, ext))):
                out.append((os.path.splitext(os.path.basename(p))[0], p))
    return out


def _components(binary: np.ndarray):
    """(heights, stats) of the connected ink components."""
    if cv2 is None:
        raise RuntimeError("fontmatch needs cv2")
    n, _lab, stats, _cent = cv2.connectedComponentsWithStats(binary, 8)
    heights = [int(stats[i][cv2.CC_STAT_HEIGHT]) for i in range(1, n)]
    return heights, stats


def _stem_width(binary: np.ndarray, cap_top: int, cap_h: float) -> float:
    """Median horizontal ink run on the scanline through the middle of
    the cap band. 0 when no run >= 2 px is found."""
    mid = int(round(cap_top + cap_h / 2))
    if mid < 0 or mid >= binary.shape[0]:
        return 0.0
    row = binary[mid, :]
    runs, cur = [], 0
    for v in row:
        if v:
            cur += 1
        elif cur:
            runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    runs = [r for r in runs if r >= 2]
    return float(np.median(runs)) if runs else 0.0


def measure_ink(binary: np.ndarray) -> Dict[str, float]:
    """The fingerprint of one ink image (binary True = ink).

    cap_h: median height of the tall components — the CAP height.
        Slashes are the tallest components but few, so the median
        ignores them (the 2026-11-24 caps-vs-slashes lesson).
    x_h: median height of the mid components (lowercase x-height).
    stem_w: median run on the cap-mid scanline.
    slash_h: tallest component (the slash/ascender height).
    ink_w / ink_h: the ink bounding box.
    """
    if not binary.any():
        return {"cap_h": 0.0, "x_h": 0.0, "stem_w": 0.0, "slash_h": 0.0,
                "ink_w": 0.0, "ink_h": 0.0}
    heights, stats = _components(binary.astype(np.uint8))
    heights = [h for h in heights if h >= 2]
    slash_h = float(max(heights)) if heights else 0.0
    tall = [h for h in heights if h >= 0.5 * slash_h]
    cap_h = float(np.median(tall)) if tall else 0.0
    mid = [h for h in heights if 0.35 * cap_h <= h <= 0.65 * cap_h] if cap_h else []
    x_h = float(np.median(mid)) if mid else 0.0
    ys, xs = np.where(binary)
    cap_top = int(ys.min())
    stem_w = _stem_width(binary, cap_top, cap_h) if cap_h else 0.0
    return {"cap_h": cap_h, "x_h": x_h, "stem_w": stem_w, "slash_h": slash_h,
            "ink_w": float(xs.max() - xs.min() + 1),
            "ink_h": float(ys.max() - ys.min() + 1)}


def fingerprint(gray: np.ndarray, box: Tuple[int, int, int, int],
                threshold: int = 150) -> Dict[str, float]:
    """Fingerprint the ink inside `box` (x0, y0, x1, y1) on a grayscale
    image. Trims to the ink bounding box first, so a loose probe region
    still measures only the letters."""
    x0, y0, x1, y1 = (max(0, int(v)) for v in box)
    sub = gray[y0:y1, x0:x1]
    binary = sub < threshold
    if not binary.any():
        return {"cap_h": 0.0, "x_h": 0.0, "stem_w": 0.0, "slash_h": 0.0,
                "ink_w": 0.0, "ink_h": 0.0}
    ys, xs = np.where(binary)
    trimmed = binary[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return measure_ink(trimmed)


def _cap_at_100(font_path: str) -> float:
    """Cap height of 'H' rendered at fs 100 — the font's cap ratio."""
    f = ImageFont.truetype(font_path, size=100)
    im = Image.new("L", (300, 300), 255)
    ImageDraw.Draw(im).text((10, 10), "H", font=f, fill=0)
    a = np.array(im)
    ys, _ = np.where(a < 120)
    return float(ys.max() - ys.min() + 1)


def _render_at_fs(font_path: str, text: str, fs: int) -> Optional[Dict[str, float]]:
    """Render `text` at integer fs and fingerprint the render."""
    f = ImageFont.truetype(font_path, size=fs)
    im = Image.new("L", (2000, 160), 255)
    ImageDraw.Draw(im).text((10, 10), text, font=f, fill=0)
    a = np.array(im)
    ys, xs = np.where(a < 120)
    if len(xs) == 0:
        return None
    trimmed = (a[ys.min():ys.max() + 1, xs.min():xs.max() + 1] < 120)
    m = measure_ink(trimmed)
    m["fs"] = float(fs)
    return m


def render_metrics(font_path: str, text: str,
                   target_cap_h: float) -> Dict[str, float]:
    """Render `text` in `font_path` at the fs whose cap height equals
    `target_cap_h`, and fingerprint the render with the same ruler as
    `fingerprint`. The cap is matched by construction; the other
    metrics are what differ between fonts.

    The fs is swept ±2 around the estimate and the render whose cap
    is closest to the target wins: fs rounding alone would otherwise
    bias every candidate's width by a few percent (a 2026-11-24
    debugging lesson — the true font must be able to score ~0)."""
    cap100 = _cap_at_100(font_path)
    if cap100 <= 0:
        raise ValueError(f"cannot measure cap height of {font_path}")
    fs0 = target_cap_h / cap100 * 100.0
    best = None
    for dfs in (-3, -2, -1, 0, 1, 2, 3):
        fs = int(round(fs0)) + dfs
        if fs < 6:
            continue
        m = _render_at_fs(font_path, text, fs)
        if m is None:
            continue
        score = abs(m["cap_h"] - target_cap_h)
        if best is None or score < best[0]:
            best = (score, m)
    if best is None:
        return {"cap_h": 0.0, "x_h": 0.0, "stem_w": 0.0, "slash_h": 0.0,
                "ink_w": 0.0, "ink_h": 0.0, "fs": fs0}
    return best[1]


# Absolute tolerance (px) per metric in distance(): stems and caps
# quantize to whole pixels, and a scan adds ~1 px of edge noise, so a
# 1 px difference is not evidence. A real weight difference is >= 2 px.
_TOL = {"cap_h": 1.0, "x_h": 1.0, "stem_w": 1.0, "slash_h": 1.0, "ink_w": 2.0}


def distance(fp: Dict[str, float], cand: Dict[str, float],
             weights: Optional[Dict[str, float]] = None) -> Tuple[float, Dict[str, float]]:
    """Weighted mean relative error between a fingerprint and a
    candidate render. Returns (distance, per-metric relative errors)."""
    w = weights or WEIGHTS
    errs, total = {}, 0.0
    for k, wk in w.items():
        ref = fp.get(k, 0.0)
        if ref <= 0:
            continue
        e = max(0.0, abs(cand.get(k, 0.0) - ref) - _TOL.get(k, 0.0)) / ref
        errs[k] = e
        total += wk * e
    denom = sum(wk for k, wk in w.items() if fp.get(k, 0.0) > 0)
    return (total / denom if denom else 0.0), errs


def rank_fonts(fp: Dict[str, float], text: str,
               candidates: Sequence[Tuple[str, str]],
               weights: Optional[Dict[str, float]] = None) -> List[Dict]:
    """Rank candidate fonts for `text` against fingerprint `fp`.
    Each entry: {name, path, distance, metrics, errors, fs}."""
    ranked = []
    for name, path in candidates:
        try:
            m = render_metrics(path, text, fp["cap_h"])
        except Exception:
            continue
        d, errs = distance(fp, m, weights)
        ranked.append({"name": name, "path": path, "distance": d,
                       "metrics": m, "errors": errs, "fs": m.get("fs", 0.0)})
    ranked.sort(key=lambda r: r["distance"])
    return ranked


def _best_iou(a: np.ndarray, b: np.ndarray, shift: int = 3) -> float:
    """Best IoU of two binary ink images over a ±`shift` px alignment
    search. Scans are never perfectly aligned with a clean render, so
    the search is part of the score."""
    H = max(a.shape[0], b.shape[0]) + 2 * shift
    W = max(a.shape[1], b.shape[1]) + 2 * shift
    A = np.zeros((H, W), bool)
    A[shift:shift + a.shape[0], shift:shift + a.shape[1]] = a
    best = 0.0
    for dy in range(-shift, shift + 1):
        for dx in range(-shift, shift + 1):
            B = np.zeros((H, W), bool)
            y0, x0 = shift + dy, shift + dx
            B[y0:y0 + b.shape[0], x0:x0 + b.shape[1]] = b
            inter = int((A & B).sum())
            union = int((A | B).sum())
            if union:
                best = max(best, inter / union)
    return best


def overlay_score(gray: np.ndarray, box: Tuple[int, int, int, int],
                  font_path: str, text: str,
                  threshold: int = 150) -> float:
    """Shape match: render `text` in `font_path` at the cap height
    measured in `box`, and score the best IoU against the scan's ink.

    This is the PRIMARY ranking signal on real scans: the component
    fingerprint degrades when scan ink spreads and letters touch
    (dot gain fattens ink_w ~7%, components merge so x_h reads 0),
    but the overlay still reads the glyph SHAPES. The fingerprint
    distance stays as a secondary signal (it works on clean renders)."""
    x0, y0, x1, y1 = (max(0, int(v)) for v in box)
    sub = gray[y0:y1, x0:x1]
    binary = sub < threshold
    if not binary.any():
        return 0.0
    ys, xs = np.where(binary)
    crop = binary[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    fp = measure_ink(crop)
    if fp["cap_h"] <= 0:
        return 0.0
    cap100 = _cap_at_100(font_path)
    if cap100 <= 0:
        return 0.0
    fs0 = fp["cap_h"] / cap100 * 100.0
    best = 0.0
    for dfs in (-3, -2, -1, 0, 1, 2, 3):
        fs = int(round(fs0)) + dfs
        if fs < 6:
            continue
        m = _render_at_fs(font_path, text, fs)
        if m is None:
            continue
        # re-render the ink at this fs for the overlay
        f = ImageFont.truetype(font_path, size=fs)
        im = Image.new("L", (2000, 160), 255)
        ImageDraw.Draw(im).text((10, 10), text, font=f, fill=0)
        a = np.array(im)
        yy, xx = np.where(a < 120)
        render = a[yy.min():yy.max() + 1, xx.min():xx.max() + 1] < 120
        best = max(best, _best_iou(crop, render))
    return best


def overlay_rank(gray: np.ndarray, box: Tuple[int, int, int, int],
                 text: str,
                 candidates: Sequence[Tuple[str, str]]) -> List[Dict]:
    """Rank candidates by overlay score (best first)."""
    ranked = []
    for name, path in candidates:
        try:
            s = overlay_score(gray, box, path, text)
        except Exception:
            continue
        ranked.append({"name": name, "path": path, "iou": s})
    ranked.sort(key=lambda r: -r["iou"])
    return ranked


def match_font(gray: np.ndarray, box: Tuple[int, int, int, int], text: str,
               bold: bool = False,
               candidates: Optional[Sequence[Tuple[str, str]]] = None,
               weights: Optional[Dict[str, float]] = None) -> Dict:
    """Fingerprint the ink in `box` and rank the fonts for `text`.
    Returns {fingerprint, ranked, best} — `best` is the closest font,
    never a claim that it IS the original's font file."""
    fp = fingerprint(gray, box)
    cands = list(candidates) if candidates is not None else available_serif_candidates()
    if bold:
        cands = [c for c in cands if "Bold" in c[0] or "Demi" in c[0]]
    else:
        cands = [c for c in cands if "Bold" not in c[0] and "Demi" not in c[0]]
    ranked = rank_fonts(fp, text, cands, weights)
    return {"fingerprint": fp, "ranked": ranked,
            "best": ranked[0] if ranked else None}
