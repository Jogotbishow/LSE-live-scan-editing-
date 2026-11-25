"""Tests for lse.fontmatch — the font fingerprint + ranking module.

Portable: every "original" here is a synthetic PIL render, no real
fixtures. The module must identify the font it was rendered in, and
must measure the CAP height (not the slash height) on slashy strings.
"""

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from lse.fontmatch import (
    _cap_at_100,
    fingerprint,
    match_font,
    rank_fonts,
    system_serif_candidates,
)


def _render_gray(font_path, text, fs):
    f = ImageFont.truetype(font_path, size=int(round(fs)))
    im = Image.new("L", (2000, 160), 255)
    ImageDraw.Draw(im).text((10, 10), text, font=f, fill=0)
    return np.array(im)


def _by_name(cands, name):
    for n, p in cands:
        if n == name:
            return p
    return None


@pytest.fixture(scope="module")
def cands():
    cs = system_serif_candidates()
    assert _by_name(cs, "NimbusRoman-Regular"), "Nimbus Roman missing"
    assert _by_name(cs, "LiberationSerif-Regular"), "Liberation missing"
    return cs


def test_identifies_nimbus_regular(cands):
    """A fake original rendered in Nimbus Roman Regular must rank
    Nimbus Roman Regular first, clearly ahead of Liberation."""
    path = _by_name(cands, "NimbusRoman-Regular")
    gray = _render_gray(path, "PLNU1072600239", 60)
    fp = fingerprint(gray, (0, 0, gray.shape[1], gray.shape[0]))
    ranked = rank_fonts(fp, "PLNU1072600239", cands)
    assert ranked[0]["name"] == "NimbusRoman-Regular"
    assert ranked[0]["distance"] < 0.08
    lib = next(r for r in ranked if r["name"] == "LiberationSerif-Regular")
    assert lib["distance"] > ranked[0]["distance"]


def test_identifies_nimbus_bold(cands):
    """Same, for Bold — the invoice weight."""
    path = _by_name(cands, "NimbusRoman-Bold")
    gray = _render_gray(path, "U2EX/2628/60024/DT.07.08.2026", 60)
    fp = fingerprint(gray, (0, 0, gray.shape[1], gray.shape[0]))
    ranked = rank_fonts(fp, "U2EX/2628/60024/DT.07.08.2026",
                        [c for c in cands if "Bold" in c[0]])
    assert ranked[0]["name"] == "NimbusRoman-Bold"
    assert ranked[0]["distance"] < 0.08


def test_caps_not_slashes(cands):
    """The 2026-11-24 lesson: the measured cap height must be the CAP
    height, even when a much taller component sits in the same box.
    (In the real Raviraj page the slashes span 55 px against 40 px
    caps; in a clean Nimbus render the '/' is only ~1 px taller than
    the caps, so the test plants a synthetic 55 px tall stroke — the
    median must ignore it.)"""
    path = _by_name(cands, "NimbusRoman-Bold")
    cap100 = _cap_at_100(path)
    fs = 40.0 / cap100 * 100.0
    gray = _render_gray(path, "U2EX/2628/60024/DT.07.08.2026", fs)
    # plant a tall thin "slash" (55 px) into the empty space at the right
    gray[5:60, 1200:1202] = 0
    fp = fingerprint(gray, (0, 0, gray.shape[1], gray.shape[0]))
    assert abs(fp["cap_h"] - 40.0) <= 2.0, f"cap_h={fp['cap_h']}"
    assert fp["slash_h"] >= 54.0, f"slash_h={fp['slash_h']}"


def test_match_font_end_to_end(cands):
    """match_font picks the right font and returns the ranking.

    Note: with Times New Roman in the default pool, a Nimbus render
    ties with Times (d=0.0000 both — the two Times clones are
    metrically identical on this string), so this plumbing test pins
    the system-only candidate list, where Nimbus must win."""
    path = _by_name(cands, "NimbusRoman-Regular")
    gray = _render_gray(path, "PLNU1072600239", 60)
    out = match_font(gray, (0, 0, gray.shape[1], gray.shape[0]),
                     "PLNU1072600239", candidates=cands)
    assert out["best"]["name"] == "NimbusRoman-Regular"
    assert len(out["ranked"]) >= 3
    assert out["fingerprint"]["cap_h"] > 0


def test_overlay_ranks_true_font_first(cands):
    """The overlay score (best IoU) must rank the true font first on
    a clean render — this is the signal that survives real scans."""
    from lse.fontmatch import overlay_rank

    path = _by_name(cands, "NimbusRoman-Regular")
    gray = _render_gray(path, "PLNU1072600239", 60)
    ranked = overlay_rank(gray, (0, 0, gray.shape[1], gray.shape[0]),
                          "PLNU1072600239", cands)
    assert ranked[0]["name"] == "NimbusRoman-Regular"
    assert ranked[0]["iou"] > 0.9
    lib = next(r for r in ranked if r["name"] == "LiberationSerif-Regular")
    assert lib["iou"] < ranked[0]["iou"]
