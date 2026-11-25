"""Tests for lse.glyphharvest — the document-is-its-own-font module.

Portable: every "document" here is a synthetic PIL render, no real
fixtures. Harvest must map components <-> characters 1:1, compose
must re-segment to the same per-letter widths (the pipeline adds no
distortion), and a character that never appears must be reported
missing, never invented.
"""

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from lse.fonts import find_font
from lse.glyphharvest import GlyphLibrary, segment_word


def _render_gray(font_path, text, fs):
    f = ImageFont.truetype(font_path, size=int(round(fs)))
    im = Image.new("L", (2000, 160), 255)
    ImageDraw.Draw(im).text((10, 10), text, font=f, fill=0)
    return np.array(im)


def _tight_box(gray):
    ys, xs = np.where(gray < 150)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


@pytest.fixture(scope="module")
def times():
    return find_font("Times New Roman")


def test_harvest_maps_1_to_1(times):
    gray = _render_gray(times, "PLNU1072600239", 57)
    lib = GlyphLibrary()
    rep = lib.add(gray, _tight_box(gray), "PLNU1072600239")
    assert rep["mismatch"] is None
    assert rep["components"] == 14
    assert rep["chars"] == 14
    assert lib.words_harvested == 1


def test_harvest_dot_sits_on_baseline(times):
    # A '.' has area ~26 px at this size — smaller than a scan speck
    # (~21 px) — so area alone cannot keep it. It stays because its
    # bottom IS the baseline; a speck floating above the line goes.
    gray = _render_gray(times, "0.0245", 57)
    lib = GlyphLibrary()
    rep = lib.add(gray, _tight_box(gray), "0.0245")
    assert rep["mismatch"] is None
    assert rep["components"] == 6
    assert "." in lib.glyphs


def test_compose_resegments_identically(times):
    gray = _render_gray(times, "PLNU1072600239", 57)
    lib = GlyphLibrary()
    lib.add(gray, _tight_box(gray), "PLNU1072600239")
    # New string uses only characters the source word has ('4' is not
    # among them — the missing-character test covers that case).
    layer, m = lib.compose("PLNU1073700239")
    white = Image.new("RGBA", layer.size, (255, 255, 255, 255))
    white.alpha_composite(layer)
    arr = np.array(white.convert("L"))
    glyphs, _ = segment_word(arr, [0, 0, arr.shape[1], arr.shape[0]])
    comp_ws = [g["w"] for g in glyphs if g["char"] is None]
    exp_ws = [l["w"] for l in m["letters"]]
    assert comp_ws == exp_ws
    # The new string reuses the old string's glyphs: P/L/N/U widths
    # are the harvested ones, not a font's.
    harvested = {l["char"]: l["w"] for l in m["letters"]}
    assert harvested["P"] == lib.glyphs["P"][0]["w"]
    assert harvested["L"] == lib.glyphs["L"][0]["w"]


def test_missing_character_reported_not_invented(times):
    gray = _render_gray(times, "PLNU1072600239", 57)
    lib = GlyphLibrary()
    lib.add(gray, _tight_box(gray), "PLNU1072600239")
    assert lib.missing("PLNU1073700249") == ["4"]
    with pytest.raises(KeyError, match="not on the page"):
        lib.compose("PLNU1073700249")


def test_spaces_measured_not_guessed(times):
    gray = _render_gray(times, "0.0230 - 0.0270", 57)
    lib = GlyphLibrary()
    rep = lib.add(gray, _tight_box(gray), "0.0230 - 0.0270")
    assert rep["mismatch"] is None
    assert rep["spaces_found"] == 2
    assert lib.space_width is not None
    assert lib.space_width > lib.median_gap()
    # Round-trip the same string: the spaces survive the compose,
    # and the width is the harvested word's width — not wider.
    # (Regression: the first compose double-counted every space,
    # once in the preceding glyph's advance and once as the space
    # item; the spec came out 123 px too wide.)
    layer, m = lib.compose("0.0230 - 0.0270")
    assert m["width_px"] > 0
    assert len(m["letters"]) == 13
    box = _tight_box(gray)
    # Within 3%: PIL's own advance rounding spreads a few px over
    # 13 glyphs. The point of the bound is the double-count, which
    # would add a whole extra space width per space (~30 px here).
    assert abs(m["width_px"] - (box[2] - box[0])) <= 0.03 * (box[2] - box[0])


def test_wide_letter_never_split(times):
    # 'U' (41 px) and 'm' (43 px) among '0's (25 px): both trip the
    # width gate (1.6 x median), and the old splitter cut them — the
    # 'U' bottom curve is 2 px thick over five columns, the 'm' arch
    # gaps are empty columns with tall stems beside them. The new
    # three-part bridge rule must leave both whole: the harvest maps
    # 5 <-> 5 with no split.
    gray = _render_gray(times, "0U0m0", 57)
    lib = GlyphLibrary()
    rep = lib.add(gray, _tight_box(gray), "0U0m0")
    assert rep["mismatch"] is None
    assert rep["components"] == 5
    assert rep["splits"] == 0
