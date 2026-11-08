#!/usr/bin/env python3
"""Track 2b — Rhythm DP: word boundaries in a gapless blob, no OCR.

Mechanism (new; NOT a gap threshold, NOT Otsu/2-means/V1):
  * Two ink profiles from the same grey crop: Otsu profile po[x] (sees ALL
    ink, incl. light print) and dark profile pd[x] (letter cores,
    <0.65*otsu). A column with ink in NEITHER mask is certainly empty.
  * Candidate cuts = midpoints of Otsu zero-runs + blob edges. (A cut may
    also fall on a dark-profile local minimum inside a piece with no Otsu
    zero column — the truly gapless join — with a cost = ink crossed.)
  * GLOBAL tiling by dynamic programming over the candidates: every column
    belongs to exactly one word, so NOTHING is dropped in the middle
    (TOP-2's silent loss is impossible by construction). Cost of a word
    [a,b): cut cost (ink crossed at its edges) + letter-rhythm cost
    (|width - k*pitch|/pitch, pitch = the page's own letter advance) +
    a large penalty if a clear (>=4px) Otsu zero-run lies strictly inside
    the word (a clear space must be a boundary) + a small per-word cost
    (prevents splitting at 1-2px speckle gaps, e.g. of|the).
  * pitch is learned from the page itself (median dark-sub width +
    median dark-sub gap of the page's clean text), never a hard-coded
    constant per document.
"""
import numpy as np


def zero_runs(prof):
    """Maximal runs of prof==0 -> list of (start, end_exclusive, length)."""
    runs, s = [], None
    for i, v in enumerate(prof):
        if v == 0 and s is None:
            s = i
        elif v != 0 and s is not None:
            runs.append((s, i, i - s)); s = None
    if s is not None:
        runs.append((s, len(prof), len(prof) - s))
    return runs


def rhythm_dp_words(bbox, gray, otsu_val, med_h, pitch,
                    p_internal=10.0, c_word=1.0, w_cut=2.0, w_rhythm=1.0,
                    clear_run=4):
    """bbox=(x0,y0,x1,y1) absolute. Returns list of word dicts
    {box:[x0,y0,x1,y1] abs, n_comp, src:'rhythm-dp'} and a debug dict."""
    x0, y0, x1, y1 = (int(v) for v in bbox)
    W, H = x1 - x0, y1 - y0
    crop = gray[y0:y1, x0:x1]
    dark_thr = int(0.65 * otsu_val)
    otsu_ink = crop < otsu_val
    dark_ink = crop < dark_thr
    # strip solid rule/underline rows (as segment.py does)
    row_ink = otsu_ink.sum(axis=1)
    keep = row_ink <= 0.90 * W
    otsu_ink = otsu_ink & keep[:, None]
    dark_ink = dark_ink & keep[:, None]
    po = otsu_ink.sum(axis=0).astype(float)
    pd = dark_ink.sum(axis=0).astype(float)

    runs = [r for r in zero_runs(po) if r[2] >= 1]
    # candidate cut positions (relative x): blob edges + zero-run midpoints
    cands = {0, W}
    forced = []  # midpoints of CLEAR runs (>=clear_run px)
    for (s, e, ln) in runs:
        mid = (s + e) // 2
        cands.add(mid)
        if ln >= clear_run:
            forced.append(mid)
    # dark-minimum candidates inside pieces with no Otsu zero column:
    # local minima of pd where po is small (<=2) — the gapless-join cut.
    # Only where the nearest clear run is far (inside a long no-zero span).
    for i in range(2, W - 2):
        if po[i] <= 2 and pd[i] <= pd[i - 1] and pd[i] <= pd[i + 1] \
                and pd[i] < pd[i - 2] + 1 and pd[i] < pd[i + 2] + 1:
            cands.add(i)
    cands = sorted(cands)
    n = len(cands)
    forced_set = set(forced)
    # prefix count of forced midpoints, for O(1) internal penalty
    forced_pref = np.zeros(W + 1, dtype=int)
    for m in forced:
        forced_pref[m] = 1
    forced_pref = np.cumsum(forced_pref)

    def cut_cost(rel_x):
        if rel_x in (0, W):
            return 0.0
        lo, hi = max(0, rel_x - 1), min(W, rel_x + 2)
        ink = min(po[lo:hi].min(), 99) + min(pd[lo:hi].min(), 99)
        return w_cut * ink / max(1.0, 2.0 * H)

    def word_cost(a, b):
        w = b - a
        if w <= 0:
            return 1e9
        k = max(1, int(round(w / pitch)))
        rhythm = abs(w - k * pitch) / pitch
        cost = w_rhythm * rhythm
        if w < 0.6 * pitch:      # narrower than one letter
            cost += 3.0
        if k > 28:               # implausibly long single word
            cost += (k - 28) * 0.5
        return cost

    INF = 1e18
    dp = [INF] * n
    back = [-1] * n
    dp[0] = 0.0
    for j in range(1, n):
        bj = cands[j]
        best, besti = INF, -1
        for i in range(j):
            ai = cands[i]
            if dp[i] >= INF:
                continue
            # forced midpoints strictly inside (ai, bj) -> penalty each
            n_in = int(forced_pref[bj - 1] - forced_pref[ai]) if bj - 1 > ai else 0
            c = dp[i] + cut_cost(ai) + word_cost(ai, bj) \
                + p_internal * n_in + c_word
            if c < best:
                best, besti = c, i
        dp[j] = best
        back[j] = besti
    # backtrack
    spans = []
    j = n - 1
    while j > 0:
        i = back[j]
        if i < 0:
            break
        spans.append((cands[i], cands[j]))
        j = i
    spans.reverse()
    # y-bounds per word from ink rows in its x-range
    words = []
    for (a, b) in spans:
        col_ink = otsu_ink[:, a:b].sum(axis=1)
        rows = np.nonzero(col_ink > 0)[0]
        if len(rows):
            wy0, wy1 = y0 + int(rows[0]), y0 + int(rows[-1]) + 1
        else:
            wy0, wy1 = y0, y1
        words.append({"box": [x0 + a, wy0, x0 + b, wy1],
                      "n_comp": max(1, int(round((b - a) / pitch))),
                      "src": "rhythm-dp"})
    dbg = {"n_candidates": n, "n_forced": len(forced), "forced": forced,
           "cost": dp[n - 1], "n_words": len(words),
           "zero_runs_ge4": [(s + x0, e + x0, ln) for (s, e, ln) in runs if ln >= clear_run]}
    return words, dbg
