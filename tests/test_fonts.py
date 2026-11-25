"""Tests for lse/fonts.py — the bundled-font resolver — and for the
engine's use of the bundled fonts.

The point (2026-11-24, the user's words): every font LSE uses must
live INSIDE LSE, so it works universally on a machine with no system
fonts installed.
"""

import os

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from lse.fontmatch import match_font
from lse.fonts import (
    BUNDLED_DIR,
    available_serif_candidates,
    bundled_candidates,
    find_font,
)

EXPECTED_BUNDLED = [
    "times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf",
    "LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf",
    "LiberationSerif-Italic.ttf", "LiberationSerif-BoldItalic.ttf",
    "NimbusRoman-Regular.otf", "NimbusRoman-Bold.otf",
    "NimbusRoman-Italic.otf", "NimbusRoman-BoldItalic.otf",
]


def test_bundled_fonts_present_and_loadable():
    for fname in EXPECTED_BUNDLED:
        p = BUNDLED_DIR / fname
        assert p.exists(), f"missing bundled font: {fname}"
        f = ImageFont.truetype(str(p), size=40)  # must not raise
        assert f.getname()[0]  # a real family name


def test_times_is_times_new_roman():
    f = ImageFont.truetype(str(BUNDLED_DIR / "times.ttf"), size=40)
    assert f.getname() == ("Times New Roman", "Regular")
    f = ImageFont.truetype(str(BUNDLED_DIR / "timesbd.ttf"), size=40)
    assert f.getname() == ("Times New Roman", "Bold")


def test_find_font_bundled_first():
    p = find_font("Times New Roman")
    assert p is not None and p.endswith("times.ttf")
    assert str(BUNDLED_DIR) in p  # the bundled copy, not a system one
    assert find_font("times") == p
    assert find_font("Times New Roman Bold").endswith("timesbd.ttf")
    assert find_font("Liberation Serif Bold").endswith(
        "LiberationSerif-Bold.ttf")


def test_find_font_passthrough_and_miss():
    real = str(BUNDLED_DIR / "times.ttf")
    assert find_font(real) == real
    assert find_font("NoSuchFontXYZ") is None
    assert find_font("") is None


def test_available_candidates_include_bundled():
    cands = available_serif_candidates()
    names = [n for n, _ in cands]
    assert "Times New Roman" in names
    assert "Times New Roman Bold" in names
    assert "Liberation Serif" in names
    assert "Nimbus Roman" in names
    # bundled first: Times New Roman must come before any system font
    assert names.index("Times New Roman") < 4


def test_engine_fallbacks_resolve_to_files():
    from lse import page, writeback

    assert os.path.exists(writeback.LIB_SERIF_REG)
    assert os.path.exists(writeback.LIB_SERIF_BOLD)
    assert os.path.exists(page.LIB_SERIF_REG)
    assert os.path.exists(page.LIB_SERIF_BOLD)


def test_matcher_ranks_times_first_on_times_render():
    """A fake original rendered in the bundled Times must rank Times
    New Roman first — the matcher now has the real font to find."""
    path = find_font("Times New Roman")
    f = ImageFont.truetype(path, size=60)
    im = Image.new("L", (2000, 160), 255)
    ImageDraw.Draw(im).text((10, 10), "PLNU1072600239", font=f, fill=0)
    gray = np.array(im)
    out = match_font(gray, (0, 0, gray.shape[1], gray.shape[0]),
                     "PLNU1072600239")
    assert out["best"]["name"] == "Times New Roman"
    assert out["best"]["distance"] < 0.08
