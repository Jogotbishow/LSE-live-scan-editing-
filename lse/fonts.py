"""Bundled-font resolver — LSE works anywhere, with no system fonts.

Every font LSE renders with lives in `lse/fonts/` (see its README).
This module resolves a font NAME to a file: the bundled copy first,
then the system paths LSE used to hard-code. Nothing in `lse/` may
assume `/usr/share/fonts/...` exists for a bundled font.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BUNDLED_DIR = Path(__file__).resolve().parent / "fonts"

# display name -> filename in BUNDLED_DIR
BUNDLED_FONTS: Dict[str, str] = {
    "Times New Roman": "times.ttf",
    "Times New Roman Bold": "timesbd.ttf",
    "Times New Roman Italic": "timesi.ttf",
    "Times New Roman Bold Italic": "timesbi.ttf",
    "Liberation Serif": "LiberationSerif-Regular.ttf",
    "Liberation Serif Bold": "LiberationSerif-Bold.ttf",
    "Liberation Serif Italic": "LiberationSerif-Italic.ttf",
    "Liberation Serif Bold Italic": "LiberationSerif-BoldItalic.ttf",
    "Nimbus Roman": "NimbusRoman-Regular.otf",
    "Nimbus Roman Bold": "NimbusRoman-Bold.otf",
    "Nimbus Roman Italic": "NimbusRoman-Italic.otf",
    "Nimbus Roman Bold Italic": "NimbusRoman-BoldItalic.otf",
    # Variable font (wght axis); PIL uses its default instance,
    # Regular 400. Retouch source (Raviraj 2026-11-24): its 'a'/'x'
    # retouched to the document's profile with both stems exact,
    # where Times' 'x' stem landed 1 px heavy.
    "Lora": "Lora-wght.ttf",
}

# Aliases people (and old code) use for the same faces.
_ALIASES: Dict[str, str] = {
    "times": "Times New Roman",
    "timesnewroman": "Times New Roman",
    "times new roman regular": "Times New Roman",
    "timesbd": "Times New Roman Bold",
    "times new roman bold": "Times New Roman Bold",
    "timesi": "Times New Roman Italic",
    "timesbi": "Times New Roman Bold Italic",
    "liberation serif regular": "Liberation Serif",
    "liberationserif-regular": "Liberation Serif",
    "liberation serif bold": "Liberation Serif Bold",
    "nimbus roman regular": "Nimbus Roman",
    "nimbusroman-regular": "Nimbus Roman",
    "nimbus roman bold": "Nimbus Roman Bold",
    "lora": "Lora",
}

# System fallbacks for faces that are NOT bundled (kept for machines
# where they exist; the bundled faces never reach this list).
_SYSTEM_PATHS: Dict[str, str] = {
    "Noto Serif": "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    "Noto Serif Bold": "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "Noto Serif Condensed": "/usr/share/fonts/truetype/noto/NotoSerif-Condensed.ttf",
    "Noto Serif Condensed SemiBold": "/usr/share/fonts/truetype/noto/NotoSerif-CondensedSemiBold.ttf",
    "C059 Roman": "/usr/share/fonts/opentype/urw-base35/C059-Roman.otf",
    "C059 Bold": "/usr/share/fonts/opentype/urw-base35/C059-Bold.otf",
    "P052 Roman": "/usr/share/fonts/opentype/urw-base35/P052-Roman.otf",
    "P052 Bold": "/usr/share/fonts/opentype/urw-base35/P052-Bold.otf",
    "DejaVu Serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "DejaVu Serif Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
}


def _norm(name: str) -> str:
    return " ".join(name.replace("_", " ").replace("-", " ").split()).lower()


def find_font(name_or_path: str) -> Optional[str]:
    """Resolve a font name (or an existing path) to a file path.

    Order: (1) an existing path passes through unchanged; (2) the
    bundled directory; (3) the system fallbacks. Returns None when
    nothing matches — the caller decides the fallback, never this
    function."""
    if not name_or_path:
        return None
    if os.path.exists(name_or_path):
        return name_or_path
    key = _ALIASES.get(_norm(name_or_path), name_or_path)
    # exact display name, then case-insensitive match on bundled names
    if key in BUNDLED_FONTS:
        p = BUNDLED_DIR / BUNDLED_FONTS[key]
        if p.exists():
            return str(p)
    for display, fname in BUNDLED_FONTS.items():
        if _norm(display) == _norm(name_or_path):
            p = BUNDLED_DIR / fname
            if p.exists():
                return str(p)
    for display, sys_path in _SYSTEM_PATHS.items():
        if _norm(display) == _norm(name_or_path) and os.path.exists(sys_path):
            return sys_path
    return None


def bundled_candidates() -> List[Tuple[str, str]]:
    """Every bundled font as (display name, path)."""
    out = []
    for display, fname in BUNDLED_FONTS.items():
        p = BUNDLED_DIR / fname
        if p.exists():
            out.append((display, str(p)))
    return out


def available_serif_candidates() -> List[Tuple[str, str]]:
    """All fonts the matcher can rank: bundled first (so the same
    files are used on every machine), then the system serifs that
    are not bundled. Deduplicated by display name."""
    out = bundled_candidates()
    seen = {_norm(n) for n, _ in out}
    for display, sys_path in _SYSTEM_PATHS.items():
        if _norm(display) not in seen and os.path.exists(sys_path):
            out.append((display, sys_path))
            seen.add(_norm(display))
    return out
