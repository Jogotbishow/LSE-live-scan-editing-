"""Caps retype rule — proposal B (DECISIONS.md).

Problem (measured R18, Track C, caps_test.py — re-measured, not assumed):
a 64 px slot fits NO font for a caps word like "AND" at the document's
cap height (37 px): DejaVu Bold needs 122 px (+58), the narrowest font
measured, Noto Sans ExtraCondensed Bold, needs 86 px (+22); it fits
only a 92 px slot. Squeezing (x-scale 0.525 / 0.744) or shrink-to-fit
(cap height 37 -> 19.4 px) breaks the cap-height match with the
neighbouring words. The Document DNA clone's own estimate agrees:
DHAKA / BANGLADESH ink measures give AND = 87-91 px at 37 px cap height.

DECISION (reversible, 2026-11-08): proposal B — NEVER force caps.
Caps are rendered only where they fit the word box; otherwise the
engine suggests the lowercase form instead (e.g. "and"), which fits
the slot and keeps the neighbours' spacing intact, at the cost of not
looking like the original caps. Proposal A (ExtraCondensed + widened
92 px slot + user confirmation) is NOT the default; it stays available
as an explicit caller opt-in (see fit_caps(..., allow_widen_slot=True)
— the caller must confirm with the user first).
"""
from PIL import ImageFont

# R18 measured numbers, kept as constants so a re-measurement can update
# them in one place. They are EVIDENCE, not tuning knobs: the rule below
# measures the actual font at the actual size instead of trusting them.
CAPS_SLOT_PX = 64            # the slot that started the investigation
EXTRACONDENSED_AND_PX = 86   # narrowest measured font for "AND" at 37 px cap
DNA_AND_PX_LO = 87           # Document DNA estimate for "AND"
DNA_AND_PX_HI = 91
MIN_SIDE_GAP_PX = 3          # proposal A needs 3 px free on each side
WIDTH_FIT_TARGET = 0.97      # live-page fitWidth: aim at 97% of box width
WIDTH_FIT_FLOOR = 0.75       # live-page fitWidth clamp floor (x fs0)


def _is_caps(text):
    """True when the replacement is (all) capitals: at least one cased
    letter, and no lowercase letter."""
    cased = [ch for ch in text if ch.isalpha()]
    return bool(cased) and all(ch.isupper() for ch in cased)


def measure_width(text, font_path, fs_px):
    """Rendered advance width (px) of ``text`` in ``font_path`` at size
    ``fs_px`` (PIL measurement — the same ruler the write-back uses)."""
    font = ImageFont.truetype(font_path, size=int(round(fs_px)))
    return float(font.getlength(text))


def fit_caps(text, font_path, fs_px, box_w_px, allow_widen_slot=False):
    """Decide how a (possibly caps) replacement fits its word box.

    Returns a dict:
      {"fits": bool, "action": "caps" | "suggest_lowercase" |
       "caps_widened_slot", "text": <text to render>,
       "suggestion": <lowercase suggestion or None>,
       "width_px": <rendered width of the rendered text>,
       "box_w_px": box_w_px, "reason": <human-readable note>}
    Rules (proposal B, reversible):
      - non-caps text: unchanged, "as_typed" action (render as typed;
        the live-page width-fit handles sizing — shrinking below fs0
        is normal for non-caps words, only caps must never shrink).
        Digit-only text ("207/9") is non-caps by definition: it has
        no cased letter, so it is never routed to the lowercase
        suggestion (an earlier build mislabelled it
        "suggest_lowercase" in the audit record).
      - caps text that fits (width <= box width): render as typed.
      - caps text that does NOT fit: NEVER squeeze, NEVER shrink the
        cap height. Suggest the lowercase form; render the suggestion
        only if the caller accepts it (``text`` is the suggestion, and
        ``suggestion`` names it — the caller decides, the engine never
        silently swaps case on an issued COA).
      - allow_widen_slot=True (proposal A, caller-confirmed only):
        caps may use a widened slot (box + 2*MIN_SIDE_GAP_PX on each
        side is NOT granted here — the caller widens the box itself and
        passes the widened width; this flag only records that the
        widening was user-confirmed).
    """
    width = measure_width(text, font_path, fs_px)
    if width <= box_w_px:
        return {"fits": True, "action": "caps", "text": text,
                "suggestion": None, "width_px": round(width, 1),
                "box_w_px": box_w_px,
                "reason": "fits the box as typed"}
    if not _is_caps(text):
        return {"fits": False, "action": "as_typed",
                "text": text, "suggestion": None,
                "width_px": round(width, 1), "box_w_px": box_w_px,
                "reason": "does not fit the box at cap-height size; "
                          "not caps, so no case suggestion applies — "
                          "render as typed, the width-fit sizes it"}
    lower = text.lower()
    lower_w = measure_width(lower, font_path, fs_px)
    if allow_widen_slot:
        return {"fits": True, "action": "caps_widened_slot", "text": text,
                "suggestion": None, "width_px": round(width, 1),
                "box_w_px": box_w_px,
                "reason": "caps kept only because the caller confirmed "
                          "a widened slot (proposal A); the engine never "
                          "widens a slot by itself"}
    # Is the lowercase suggestion itself renderable? The live page /
    # write-back width-fit scales every word to 97% of its box, clamped
    # to [0.75, 1.25] x fs0. The suggestion is renderable iff, at the
    # 0.75 floor, it still fits INSIDE the box (the 97% is a target,
    # not a requirement). (Measured: "and" in the DNA clone renders
    # 62.1px at the floor — inside a 64px box; caps "AND" renders
    # 79.9px at the floor — outside it. That is the
    # mechanism-grounded difference between the two cases.)
    need_scale = (WIDTH_FIT_TARGET * box_w_px) / lower_w if lower_w > 0 else 1.0
    return {"fits": False, "action": "suggest_lowercase", "text": lower,
            "suggestion": lower, "width_px": round(lower_w, 1),
            "box_w_px": box_w_px,
            "suggestion_scale": round(need_scale, 3),
            "suggestion_fits_via_width_fit": bool(lower_w * WIDTH_FIT_FLOOR <= box_w_px),
            "reason": f"caps {width:.0f}px does not fit a {box_w_px:.0f}px "
                      f"box (R18: narrowest caps font needs "
                      f"{EXTRACONDENSED_AND_PX}px for 'AND' in a "
                      f"{CAPS_SLOT_PX}px slot); lowercase suggested "
                      f"instead — never squeezed, never shrunk"}
