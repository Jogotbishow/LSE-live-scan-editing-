"""Track D — heading detection (Round 3, Track D, item 1).

Image-only heading signals (no OCR text anywhere in this module):
  H1 grey-bar line: the band behind a line's words is far greyer than
     paper — the title sits on a grey highlight bar (Aug bar ~184 grey,
     May bar halftone-dithered). Rule: line band mean grey (non-Otsu-ink
     pixels, band = line bbox +/-3px y, +/-4px x) < 220.
     Measured separation: title 195.5 (Aug) / 203.4 (May) vs next-lowest
     line on the page 234.9 (Aug) / 243.2 (May). Threshold 220 sits
     mid-gap on both pages (margins 16.6 / 14.9 grey levels).
  H2 table-header line: the first text line below the table's top rule.
     Table rules are the page's dominant horizontals: rule bands are
     consecutive rows with a >=300px run of pixels < 210 grey; band
     strength = longest run in the band. Table bands reach 0.64-0.68x
     the page's longest rule; header-block rules only 0.50-0.51x.
     Rule: table band = strength > 0.58 x page-max strength; top rule =
     first such band (smallest y); header line = line with the smallest
     top below that band.
     Measured margins: Aug table-min 660 vs thr 597 (63px), header-block
     max 529 vs thr 597 (68px); May table-min 1009 vs thr 856 (153px),
     header-block max 742 vs thr 856 (114px).

NOT used (measured and rejected — see explore_lines.py /
explore_bold_lines.py):
  * word/line height — title h (Aug 19) equals body median; 75/293 Aug
    and 88/279 May body words are >= 21px tall.
  * line median stroke ratio — Aug header line 0.158 < body line 11
    (0.182); May header 0.149 < body line 34 (0.158). Overlaps.
  * "line contains a stroke-bold word" — nearly every line does
    (residual over-bold body words + tiny-sliver artefacts).
  * rule x-extent — every rule band spans the full page width (~1472px).
  * single absolute run-length threshold — Aug needs thr in (529,660],
    May needs thr in (742,1009]; no single value works.

CAVEAT: H2's 0.58 factor is fitted on these two pages of one COA
template. It is validated here (both pages, zero false lines) but must
be re-validated on other documents (Round 3 Track B coverage) before
being trusted generally.
"""
import numpy as np

H1_GREY_THR = 220
H2_FRAC = 0.58
RULE_GREY = 210
RULE_MIN_RUN = 450  # 300 x 1.5 (300 DPI)
# Round 10 (B): dithered header-bar arm — the Aug E-mail/Website header
# line is the same bold printed line on all 8 Aug pages, but bar_ink
# flags it on only 2 (threshold luck: header bar_ink 0.107-0.176 vs
# non-header max 0.143, gap 0.010). gap_dark = fraction of inter-word
# gap pixels with grey < 235 (halftone dither; paper ~249). Measured
# margins on all 14 PG pages, both r8m and r9m families: gap_dark
# header min 0.195 vs non-header max 0.116 (gap +0.079); bar_ink
# among gap_dark>=0.15 lines: header min 0.107 vs non-header max
# 0.037 (gap +0.070). Midpoints 0.155 / 0.072. Admits exactly the
# 8 Aug header lines and nothing else. Replaces the Round 9 §5.3
# documented override (Aug p2 e-mail merge workaround).
GAP_DARK_THR = 0.155
GAP_BAR_THR = 0.072
# Round 11 Track A (R1): exemplar arm — merge-invariant replacement for
# the gap_dark arm's www-merge failure. The 8 Aug E-mail/Website header
# lines are the SAME physical printed line (eye-checked 3x); on r10m
# their ink matches the aug-p1 exemplar at IoU 0.704-1.000, while the
# highest Aug non-header line matches at 0.298. The same TEXT also
# occurs on the 6 May pages (IoU 0.678-0.748) but WITHOUT the wash bar
# (band_grey 248.6-249.8 vs header 233.4-237.2, eye-checked: May line
# sits on plain white paper), so identity alone cannot separate them —
# the arm needs BOTH signals. Thresholds are midpoints of measured
# gaps: IoU (0.704+0.298)/2 = 0.501; grey (237.2+248.6)/2 = 242.9.
# Measured over all 14 PG pages x r8m/r9m/r10m families (561 lines
# each) + Otsu +/-5 + band shift +/-1px: header IoU min 0.704, and
# the arm adds ZERO false H1 lines. The exemplar is selected
# deterministically from the document set itself (no hard-coded page):
# among lines already flagged H1 by the current arms with
# band_grey >= 220 (non-title-bar (B) lines), the one with max
# gap_dark. If no such line exists the arm is simply inactive
# (graceful fallback to the current arms). The template crop is the
# exemplar line's band (top-3..bot+3, x0-4..x1+4); seg merges cannot
# change the ink, only the crop extent by a few px, and the +-25/+-8
# anchor search absorbs page scan offsets (header anchors vary
# x 824-837, y 398-413 across the 8 Aug pages).
EXEMPLAR_IOU_THR = 0.50
EXEMPLAR_GREY_THR = 242.0
EXEMPLAR_DX = 25
EXEMPLAR_DY = 8


def _longest_run(row_bool):
    best = cur = 0
    for v in row_bool:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def rule_bands(gray):
    """Bands of consecutive rows each holding a >=RULE_MIN_RUN run of
    pixels darker than RULE_GREY. Returns [(y0, y1, max_run)]."""
    dark = gray < RULE_GREY
    bands, cur = [], None
    for y in range(gray.shape[0]):
        r = _longest_run(dark[y])
        if r >= RULE_MIN_RUN:
            if cur is None:
                cur = [y, y, r]
            else:
                cur[1] = y
                cur[2] = max(cur[2], r)
        else:
            if cur is not None:
                bands.append(tuple(cur))
                cur = None
    if cur is not None:
        bands.append(tuple(cur))
    return bands


def build_header_exemplar(pages):
    """pages: list of (gray, otsu_t, lines) for one document set.
    Returns the header exemplar template (float32 ink mask) or None.
    Selection: H1-flagged lines with band_grey >= 220, max gap_dark.
    No OCR anywhere; the template is raw ink, matched by IoU."""
    best = None
    for gray, otsu_t, lines in pages:
        base = heading_lines(gray, otsu_t, lines)
        for ln in sorted(base["h1"]):
            d = base["diag_lines"][ln]
            if d["band_grey"] >= 220 and (best is None or d["gap_dark"] > best[0]):
                best = (d["gap_dark"], gray, otsu_t, lines[ln])
    if best is None:
        return None
    _, gray, otsu_t, rs = best
    top = min(r["box"][1] for r in rs)
    bot = max(r["box"][3] for r in rs)
    x0 = max(0, min(r["box"][0] for r in rs) - 4)
    x1 = max(r["box"][2] for r in rs) + 4
    return (gray[max(0, top - 3):bot + 3, x0:x1] < otsu_t).astype(np.float32)


def exemplar_best_iou(gray, otsu_t, lines, template):
    """Best ink-IoU of template vs page ink near each line's own anchor.
    Returns {line_id: best IoU}. Uses matchTemplate (intersection) +
    an integral image (window ink count) — one pass per page."""
    import cv2 as _cv2
    ink = (gray < otsu_t).astype(np.float32)
    th, tw = template.shape
    inter = _cv2.matchTemplate(ink, template, _cv2.TM_CCORR)
    integ = _cv2.integral(ink)
    win = (integ[th:, tw:] - integ[:-th, tw:]
           - integ[th:, :-tw] + integ[:-th, :-tw])
    tc = float(template.sum())
    union = tc + win - inter
    with np.errstate(divide="ignore", invalid="ignore"):
        iou = np.where(union > 0, inter / np.maximum(union, 1e-9), 0.0)
    out = {}
    for ln, rs in lines.items():
        ay = max(0, min(r["box"][1] for r in rs) - 3)
        ax = max(0, min(r["box"][0] for r in rs) - 4)
        y_lo, y_hi = max(0, ay - EXEMPLAR_DY), min(iou.shape[0], ay + EXEMPLAR_DY + 1)
        x_lo, x_hi = max(0, ax - EXEMPLAR_DX), min(iou.shape[1], ax + EXEMPLAR_DX + 1)
        out[ln] = (float(iou[y_lo:y_hi, x_lo:x_hi].max())
                   if y_hi > y_lo and x_hi > x_lo else 0.0)
    return out


def heading_lines(gray, otsu_t, lines, exemplar=None):
    """lines: {line_id: [raw word dicts with 'box']}.
    Returns dict with:
      h1: set of line ids whose band is a grey highlight bar
      h2: line id of the table-header line (or None)
      diag: per-line diagnostics + rule-band table for the report.
    exemplar: header ink template from build_header_exemplar() for the
    same document set, or None (arm inactive). When given, the R1 arm
    (exemplar IoU >= 0.50 AND band_grey < 242) also flags H1 lines.
    This replaces the r9m-heading workaround: heading can now be
    computed from the CURRENT (r10m) segs.
    """
    diag_lines = {}
    h1 = set()
    ious = exemplar_best_iou(gray, otsu_t, lines, exemplar) if exemplar is not None else {}
    for ln, rs in lines.items():
        top = min(r["box"][1] for r in rs)
        bot = max(r["box"][3] for r in rs)
        x0 = max(0, min(r["box"][0] for r in rs) - 4)
        x1 = max(r["box"][2] for r in rs) + 4
        band = gray[max(0, top - 3):bot + 3, x0:x1]
        ink = band < otsu_t
        nonink = band[~ink]
        bgrey = float(nonink.mean()) if nonink.size else 255.0
        # 300-DPI FIX H1b: ink fraction of the band OUTSIDE word boxes
        # (a halftone bar dithers the gaps; bold letters do not).
        _y0b = max(0, top - 3)
        _outside = np.ones(band.shape, dtype=bool)
        for _r in rs:
            _outside[max(0, _r["box"][1] - _y0b):_r["box"][3] - _y0b,
                     max(0, _r["box"][0] - x0):_r["box"][2] - x0] = False
        _bar_ink = float(ink[_outside].mean()) if _outside.sum() else 0.0
        # Round 10 (B): gap_dark — dither in the inter-word gaps.
        _boxes = sorted((r["box"] for r in rs), key=lambda b: b[0])
        _gap = np.zeros(band.shape, dtype=bool)
        for _a, _b in zip(_boxes, _boxes[1:]):
            _gx0, _gx1 = _a[2] - x0, _b[0] - x0
            if _gx1 - _gx0 >= 3:
                _gap[max(0, top - _y0b):bot - _y0b, _gx0:_gx1] = True
        _gap_px = band[_gap]
        _gap_dark = float((_gap_px < 235).mean()) if _gap_px.size else 0.0
        diag_lines[ln] = {"cy": float(np.median(
            [(r["box"][1] + r["box"][3]) / 2 for r in rs])),
            "band_grey": round(bgrey, 1), "bar_ink": round(_bar_ink, 3),
            "gap_dark": round(_gap_dark, 3), "top": top, "bot": bot,
            "exemplar_iou": round(ious.get(ln, 0.0), 3)}
        if (bgrey < H1_GREY_THR or _bar_ink > 0.15
                or (_gap_dark >= GAP_DARK_THR and _bar_ink >= GAP_BAR_THR)
                or (exemplar is not None and ious.get(ln, 0.0) >= EXEMPLAR_IOU_THR
                    and bgrey < EXEMPLAR_GREY_THR)):
            h1.add(ln)
    bands = rule_bands(gray)
    page_max = max((b[2] for b in bands), default=0)
    thr = H2_FRAC * page_max
    table_bands = [b for b in bands if b[2] > thr]
    h2 = None
    top_rule = table_bands[0] if table_bands else None
    if top_rule is not None:
        below = [(min(r["box"][1] for r in rs), ln)
                 for ln, rs in lines.items()
                 if min(r["box"][1] for r in rs) > top_rule[1]]
        if below:
            h2 = min(below)[1]
    return {"h1": h1, "h2": h2, "top_rule": top_rule,
            "rule_thr": round(thr, 1), "page_max_run": page_max,
            "bands": bands, "diag_lines": diag_lines}


def heading_lines_guarded(gray, otsu_t, lines, exemplar=None):
    """Track C Round 4 -- H2 guard (merged, 300 DPI).

    Takes heading_lines() output and re-picks H2 with structural guards:
    the header line must be wide (>=0.82x page), have >=6 boxes, follow a
    short previous line (<=5 boxes, <0.60x page wide), and sit below the
    first rule band that is strong enough (>=0.25x page-max run) and below
    the title. Title = H1 if found, else the greyest line in the title
    zone (cy 450-840 at 300 DPI, i.e. Track C's [300,560] x1.5) that is
    clearly darker than the next line (>=3.0 grey levels).
    Measured Round 4 Track C (200 DPI): correct H2 on 14/14 PG pages
    (Aug p4 via the greyest-fallback). fontfix-verify stays 35/35.
    Caveat: the width margin is only 38px and the rule is PG-template
    shaped, not universal.
    Round 11 merge: exemplar is forwarded to heading_lines() so the R1
    arm (exemplar IoU + wash) also feeds H1 here; H2 re-verified 14/14
    with the exemplar at merge (Track A verified H2 14/14 without it).
    """
    base = heading_lines(gray, otsu_t, lines, exemplar=exemplar)
    h1, bands = base["h1"], base["bands"]
    diag = base["diag_lines"]
    page_w = gray.shape[1]
    page_max = base["page_max_run"]
    if h1:
        title_bottom = max(max(r["box"][3] for r in lines[ln]) for ln in h1)
        title_src = "H1"
    else:
        # fallback: greyest line in the title zone, if clearly darker
        zone = [(d["band_grey"], ln) for ln, d in diag.items()
                if 450 <= d["cy"] <= 840]
        zone.sort()
        if len(zone) >= 2 and zone[0][0] <= zone[1][0] - 3.0:
            title_bottom = max(r["box"][3] for r in lines[zone[0][1]])
            title_src = "greyest-fallback"
        else:
            title_bottom = 0
            title_src = "none"
    w_min = 0.82 * page_w
    prev_w_max = 0.60 * page_w
    band_min_run = 0.25 * page_max if page_max else 0

    def _geom(ln):
        rs = lines[ln]
        return (len(rs), max(r["box"][2] for r in rs) - min(r["box"][0] for r in rs))

    ordered = sorted(lines, key=lambda ln: min(r["box"][1] for r in lines[ln]))
    h2, top_rule, tried = None, None, []
    for band in bands:
        if band[0] <= title_bottom or band[2] < band_min_run:
            continue
        below = [ln for ln in ordered
                 if min(r["box"][1] for r in lines[ln]) > band[1]]
        if not below:
            continue
        cand = below[0]
        n, w = _geom(cand)
        ci = ordered.index(cand)
        prev = _geom(ordered[ci - 1]) if ci > 0 else (0, 0)
        tried.append({"band": band, "cand": cand, "n": n, "w": w, "prev": prev})
        if w >= w_min and n >= 6 and prev[0] <= 5 and prev[1] < prev_w_max:
            h2, top_rule = cand, band
            break
    out = dict(base)
    out.update({"h2": h2, "top_rule": top_rule, "title_bottom": title_bottom,
                "title_src": title_src, "h2_guarded_tried": tried,
                "h2_w_min": round(w_min, 1), "h2_prev_w_max": round(prev_w_max, 1)})
    return out
