# Bundled fonts — LSE works anywhere, with no system fonts installed

LSE renders replacement text with real font files. Those files live
HERE, inside the repo, so a machine with no fonts installed still
renders exactly the same way. Nothing in `lse/` may depend on a
`/usr/share/fonts/...` path for a font that is bundled here — the
resolver in `lse/fonts.py` looks in this directory FIRST and only
falls back to system paths for fonts that are not bundled.

## What is bundled (13 files)

| Family | Files | Source | Licence |
|--------|-------|--------|---------|
| Times New Roman | times.ttf, timesbd.ttf, timesi.ttf, timesbi.ttf | Microsoft Core Fonts (`times32.exe`, SourceForge `corefonts` project, 2000 release) | Microsoft Core Fonts EULA — redistributable unmodified |
| Liberation Serif | LiberationSerif-{Regular,Bold,Italic,BoldItalic}.ttf | system Liberation fonts (this machine) | SIL Open Font License 1.1 |
| Nimbus Roman | NimbusRoman-{Regular,Bold,Italic,BoldItalic}.otf | URW base35 (this machine) | GNU GPL v2 with font exception |
| Lora | Lora-wght.ttf (variable font, wght axis; default instance Regular 400) | Google Fonts (`google/fonts`, ofl/lora) | SIL Open Font License 1.1 |

## Why Lora matters

Glyph retouch (Raviraj 2026-11-24): the page has no lowercase 'a'
or 'x', so harvest cannot supply them. Retouch reworks the closest
font's glyphs toward the document's measured profile. Lora's 'a' and
'x' retouched with both stems exact (Times' 'x' landed 1 px heavy),
so Lora is the bundled retouch source for those letters.

## Why Times New Roman matters

The Raviraj supplier COAs (and most Excel-made COAs in the industry)
are set in Times New Roman. LSE used to fall back to Liberation Serif,
which is metric-compatible but NOT shape-identical — the user's eye
caught it on the PLNU batch number (2026-11-24). With the real Times
files bundled, LSE renders the document's own font.

## Adding a font

Drop the .ttf/.otf into this directory and add its display name to
`BUNDLED_FONTS` in `lse/fonts.py`. The fontmatch matcher picks it up
automatically through `available_serif_candidates()`.
