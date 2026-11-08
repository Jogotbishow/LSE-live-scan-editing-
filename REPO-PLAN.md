# LSE open-source repo — plan (staging, not yet published)

**Goal (user, 2026-11-06):** LSE stays in GRAVORA *and* becomes a standalone public GitHub repo so everyone can learn about it, contribute, and use it.

## Decisions needed from the user
- [ ] License: MIT proposed (LICENSE file drafted). Alternative: Apache-2.0.
- [ ] Repo name: `live-scan-editing` proposed.
- [ ] GitHub account/org to own the repo (his account — verify identity with `get_me` before creating).

## What goes in (code snapshot — take AFTER Round 6 finishes, so the repo ships the latest stable state)
- `lse/`: segment.py (v4-300), inpaint.py (v4), build_page300.py, heading.py (v4-300), rotate_detect.py, matcher, DNA font builder (dna-build-prod.py, vtracer-based), lse_writeback_300.py, lse_db.py, verify scripts (fontfix_verify300.py, verify_round2_300.py, repro300.py, manual_proof300.py, verify_rebuild_300.py, verify_track_c_r5.py, keymgmt_proof.py)
- `docs/`: RESEARCH.md, REPORT.md, REPORT-MAY.md, IMPROVE-REPORT.md, IMPROVE-RESEARCH.md, ROUND2/3/4/5-REPORT.md (+ ROUND6 when done), LICENCE-GROUNDWORK.md
- `demo/`: sample document + built live page (see below)

## What stays OUT (never public)
- The real PG Foils supplier COAs (Aug/May PDFs + scans) — real supplier documents with real lot numbers, quantities, company names.
- The real Raviraj / Amcor supplier documents.
- `lse_gravora.db` with real delivery records.
- Any credentials, keys, or personal data.

## Sample document (to be made before the code push)
A synthetic sample COA scan (fake company, fake lot numbers, same layout family as a real COA) rendered to PDF at 300 DPI, run end-to-end through the pipeline to prove the repo's demo works from a clean checkout. No real supplier data.

## Publish sequence (user's instruction, 2026-11-06)
1. License: **MIT — decided** (user delegated the choice to Muse; MIT chosen: simplest, most adopted, matches vtracer's MIT option).
2. **Finish the LSE build completely first — do NOT create the repo mid-build.** (Round 6 is running now; completion is judged together when the rounds report no open items left.)
3. When LSE is complete: create the GitHub repo (approval card for `create_repository`) with README + LICENSE.
4. Take the code snapshot of the completed build, build the sample demo, test from a clean checkout, push.
5. Announce: README + round reports are the announcement.

## Notes
- GitHub OAuth: connected (verified 2026-11-06). Repo creation needs the user's approval on the card.
- Licence caution (not legal advice): vtracer is MIT OR Apache-2.0 (verified verbatim); US patent US20150332491A1 exists (enforceability unverified — legal check needed before any sale). Keep the disclaimer in the reports.
