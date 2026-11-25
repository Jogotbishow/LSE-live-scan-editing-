"""Tests for lse.glyphretouch — the Photoshop layer of glyph harvest.

Portable: synthetic PIL renders only. A retouched glyph must land
within 1 px of its measured width/height/stem targets, must be
marked retouched (never mistaken for harvested ink), and compose()
must prefer a harvested glyph over a retouched one for the same
character.
"""

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from lse.fonts import find_font
from lse.glyphharvest import GlyphLibrary
from lse.glyphretouch import (
    measure_stem,
    retouch_glyph,
    retouch_into_library,
    width_factor,
)


def _render_gray(font_path, text, fs):
    f = ImageFont.truetype(font_path, size=int(round(fs)))
    im = Image.new("L", (2000, 160), 255)
    ImageDraw.Draw(im).text((10, 10), text, font=f, fill=0)
    return np.array(im)


def _tight_box(gray):
    ys, xs = np.where(gray < 150)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


@pytest.fixture(scope="module")
def lib():
    times = find_font("Times New Roman")
    out = GlyphLibrary()
    for text in ("PLNU1072600239", "0.025mm Aluminium Foil/6-8 GSM",
                 "73.04", "0.0245"):
        gray = _render_gray(times, text, 57)
        rep = out.add(gray, _tight_box(gray), text)
        assert rep["mismatch"] is None, rep
    return out


def test_retouch_lands_on_targets(lib):
    lora = find_font("Lora")
    factor, _ = width_factor(lib, lora, lib.cap_height(), like="a")
    assert factor is not None and 0.5 < factor < 1.5
    reps, miss = retouch_into_library(lib, lora, ["a", "x"])
    assert miss == []
    assert len(reps) == 2
    for r in reps:
        assert abs(r["achieved_w_px"] - r["target_w_px"]) <= 1
        assert abs(r["achieved_h_px"] - r["target_h_px"]) <= 1
        assert r["achieved_stem_px"] is not None
        assert abs(r["achieved_stem_px"] - r["target_stem_px"]) <= 1


def test_retouched_marked_and_harvest_preferred(lib):
    # 'a' is retouched; 'm' is harvested. Compose must use the
    # harvested 'm' and mark only the retouched letters.
    assert lib.retouched_chars("max") == ["a", "x"]
    layer, m = lib.compose("2 max")
    by_char = {l["char"]: l["retouched"] for l in m["letters"]}
    assert by_char["m"] is False
    assert by_char["a"] is True
    assert by_char["x"] is True


def test_measure_stem_reads_a_straight_stem(lib):
    # The harvested 'l' is a straight stem with a foot serif: its
    # measured stem (the vertical stroke) is much narrower than the
    # whole glyph width, and sits in the 3–7 px range at this size.
    l = lib.glyphs["l"][0]
    stem = measure_stem(l["bitmap"])
    assert stem is not None
    assert 3.0 <= stem <= 7.0
    assert stem < l["w"]


def test_retouch_never_halves_the_glyph(lib):
    # Regression: the first retouch run scaled 1x targets against a
    # 2x render and halved every glyph (w 11 for target 21.7).
    lora = find_font("Lora")
    bitmap, rep = retouch_glyph(lora, "a", 20.0, 30.0, 5.0, 40.0)
    assert rep["achieved_w_px"] >= 18
    assert rep["achieved_h_px"] >= 28
    assert bitmap.shape[0] >= 28
