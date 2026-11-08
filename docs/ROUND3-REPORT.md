# LSE Round 3 — চূড়ান্ত রিপোর্ট (Consolidation)

**তারিখ:** ২০২৬-১১-০৬ · **পাতা:** PG Foils supplier COA — August (রঙিন) ও May (B&W) · **স্থিতি: সম্পূর্ণ**
**প্রযুক্তির নাম: LSE — Live-Scan Editing**
**ফাইল:** `scan-paper/improve/ROUND3-REPORT.md` · **সূত্র:** `improve/round3/`-এর ৪টি ট্র্যাক-রিপোর্ট + merge রিপোর্ট + consolidation-এ নিজে চালানো যাচাই

## ০. এক লাইনে

Round 3-এর ৪টি ট্র্যাক + merge + native-৩০০ rebuild — সব মাপা হয়েছে, আর consolidation-এ পুরো স্যুট **নিজে আবার চালিয়ে** নিশ্চিত করা হয়েছে: **fontfix-verify ৩৫/৩৫ (Round 2-র ৩১/৩৫ থেকে বেড়েছে — May title + PARAMETERS bold ঠিক), verify_round2 ১৮/১৮, repro PASS, manual_proof ১০/১০, identity probe ৬/৬, rebuild verify ৪০/৪০** — কোনো regression নেই। LSE এখন: per-word cap-height sizing + heading detection + Sans fallback সহ v7 live পাতা, native-৩০০-DPI PDF write-back (মূল byte-ই ব্যাকগ্রাউন্ড) + hash-chain সহ SQLite DB রেকর্ড। তবে তিনটি সৎ কথা: **(১)** Track A-র লক্ষ্য পুরোপুরি মেলেনি — DNA WIDTH-এ Aug-এ শুধু tie, May-এ হারে (কারণ এখন DNA clone-এর digit advance, sizing নয়); **(২)** Track D-র H2 নিয়ম নতুন পাতায় ভাঙে (১৪ পাতায় ৪/১৪) — ৩৫/৩৫ শুধু দুটি p1 পাতায় সত্য; **(৩)** universality প্রমাণিত হয়নি — ভিন্ন নথিতে (Raviraj) pipeline যেমন-আছে চলে না, আর Track B native DPI কোথাও ধরে রাখেনি।

> ⚠️ **আইনি দাবিত্যাগ:** এই রিপোর্ট কারিগরি গবেষণা, আইনি পরামর্শ নয়। লাইসেন্স/পেটেন্টের অংশ (§৫) পড়ে কোনো সিদ্ধান্ত নেওয়ার আগে একজন আইনজীবীর সঙ্গে পরামর্শ বাধ্যতামূলক।

> **স্থায়ী নিয়ম (ব্যবহারকারী, ২০২৬-১১-০৬ — UNIVERSAL):** নথির FULL originality রক্ষা করতে হবে — মূল নথি যে DPI-তে আছে, সেই DPI-তেই কাজ করতে হবে; কখনো downscale নয়, ব্যাকগ্রাউন্ড কখনো re-encode নয়, resolution কখনো বদল নয়। **এটি সব ধরনের নথি, সব DPI, সব স্ক্যানের ক্ষেত্রে প্রযোজ্য, শুধু PG COA নয়।** কোনো ধাপে আসল কারণে originality রক্ষা করা না গেলে চুপচাপ মান কমানো যাবে না — সৎভাবে জানাতে হবে।

---

## ১. ট্র্যাক-ভিত্তিক before / after (সব সংখ্যা মাপা)

### Track A — WIDTH সংখ্যার sizing (per-word cap-height) — **লক্ষ্য পুরোপুরি মেলেনি, বাধা চিহ্নিত**

| শব্দ | আগে (matcher, /0.85) | পরে (matcher v3, live-fit) | রায় |
|---|---|---|---|
| Aug WIDTH "780.0" | DNA 0.503 (৫ম/শেষ) | DNA **0.446 (১ম)** — Serif Bold 0.443, ব্যবধান মাত্র 0.003 | **টাই** — ±1px shift-এ র‍্যাঙ্ক উল্টে যায় (DNA ২/৭, Serif Bold ৪/৭) |
| May WIDTH "670.0" | DNA 0.385 (৫ম/শেষ) | DNA 0.490 (৩য়); Sans Bold **0.563 (১ম)** | **হার** — Sans Bold ৭/৭ shift-এ জেতে |
| Aug Lot / May Lot | DNA 0.536 / 0.513 (১ম) | DNA 0.478 / 0.501 (১ম) | ✓ জয় ধরে রাখা |
| TEST / REPORT ×২ পাতা | DNA Bold ১ম (৪/৪) | DNA Bold ১ম (৪/৪) | ✓ জয় ধরে রাখা |

- **নতুন নিয়ম:** `fs0 = cap_h(word) / 0.70` (DNA cap height ৭০০ unit); cap-like না হলে লাইনের cap height (page-median fallback); skew-সংশোধিত classification (Aug +0.26°, May +0.11°); fitWidth clamp floor 0.75 → **0.60** (absolute floor প্রায় একই: ১৬.৩ বনাম ১৬.৮ scan px — long-replacement প্রমাণসহ)।
- **Sizing প্রমাণিত সঠিক:** DNA-র WIDTH raster-fit Aug 0.503 → **0.700**; live পাতায় WIDTH fontSize +৫.৯% (Aug), width ratio ০.৯৭ → **১.০০**; চোখে "781.5" এখন আসল "780.0"-র সমান দেখায় (আগে স্পষ্ট ছোট ছিল)।
- **আসল বাধা এখন sizing নয় — DNA clone-এর digit advance ~১০% বেশি চওড়া:** Aug WIDTH-এ DNA মোট glyph ink ৫৬ বনাম আসল ৫১ (+৯.৮%); per-glyph আকৃতি DNA-ই সেরা (single-glyph IoU 0.712)। May B&W-তে binary স্ক্যান stroke মোটা করে — Sans Bold-এর আকৃতি ভালো মেলে (glyph IoU 0.710 বনাম DNA 0.613)। Rendered cap height এখনও −৮% (১৭.৫ বনাম ১৯ px) — fitWidth চওড়া advance মেলাতে size কমায়।
- **Matcher v3:** প্রধান মেট্রিক এখন live-fit IoU (Round-2 raster-fit অস্থির প্রমাণিত: ±2px-এ ০.৪৩–০.৬৮ দোলে)।
- **কোনো regression নেই:** fontfix-verify ৩১/৩৫, verify_round2 ১৮/১৮, repro PASS, manual ১০/১০, identity ৬/৬।

### Track B — Multi-page + multi-document coverage — **PG ফরম্যাটে ধরে, universality প্রমাণিত নয়**

**PG পাতা (হাতে-গোনা sample, test-table rows ০১–০৫, প্রতি পাতায় ৩৭টি সত্য শব্দ):**

| পাতা | মোট শব্দ | Sample | পাতা | মোট শব্দ | Sample |
|---|---|---|---|---|---|
| Aug p2 | ২৯৩ | **৩৭/৩৭** (+১ speck FP) | May p2 | ২৭৫ | **৩০/৩৭** (৬ merge) |
| Aug p3 | ২৯২ | **৩৭/৩৭** | May p3 | ২৭৪ | **২৯/৩৭** (৫ merge; title ANALYTICAL+TEST এক বাক্সে) |
| Aug p4 | ২৯৩ | **৩৭/৩৭** | May p4 | ২৮১ | **৩৩/৩৭** (৪ merge; title REPORT ভেঙে "REP"+"ORT") |
| Aug p5 | ৩০৭ | **৩৭/৩৭** (+১৪ signature-stroke "শব্দ") | May p5 | ২৭২ | **৩০/৩৭** (৫ merge) |
| Aug p6 | ২৯২ | **৩৭/৩৭** (+১ speck; title "REPOR"+"T") | May p6 | ২৭৬ | **৩৩/৩৭** (৩ merge; title পুরোটা এক বাক্সে) |
| Aug p7 | ২৯৭ | **৩৭/৩৭** | | | |
| Aug p8 | ২৯৯ | **৩৭/৩৭, কিন্তু ৪টি over-split** | | | |

- **Identity probe — ৩ পাতা, সব PASS:** Aug p2 (Lot 207/9 + WIDTH 776.5, "Hard" অক্ষত), Aug p8 (Lot 380/8 + WIDTH প্রথম অর্ধেক `700.` → `701.5` — দ্বিতীয় অর্ধেক `0` অক্ষত, সেলে `701.5 0` — split defect চোখে প্রমাণিত), Raviraj p1 ঘোরানো (Consignment Date 09.08.2026 + No.-র প্রথম অর্ধেক `40001` → `40002`, দ্বিতীয় অর্ধেক `02246` অক্ষত)।
- **নতুন defect (PG পাতায়):** (১) Aug p5 — signature row ধরা পড়েনি (tall component মাত্র ১টি, শর্ত ≥২) → **১৪টি ভুয়া "শব্দ"** (সইয়ের ওপর টাইপ করা যেত — আসল ঝুঁকি); (২) Aug p8 — observation মান দশমিকে ভাঙা (`700.0`→`700.`+`0`, `0.0254`→`0.`+`0254` — শুধু observation কলাম); (৩) title blob-split ভঙ্গুর — ১২ নতুন পাতায় পরিষ্কার ৭, ভাঙা ৩, মেশা ২; (৪) speck FP (Aug p2/p6/p8); (৫) May merge systematic (২৯–৩৩/৩৭ — p1-এর ৩৩/৩৭ ব্যতিক্রম নয়, গড়)।
- **Raviraj (consignment note, ভিন্ন নথি):** যেমন-আছে **সম্পূর্ণ ব্যর্থ** — পাতা ৯০° ঘোরানো অবস্থায় store করা, rotation detection নেই → **১,০৪৭টি ভুয়া "শব্দ"**। হাতে ৯০° CW ঘুরিয়ে: ৫৪৬ শব্দ, sample R1 **২২/২৪**; কিন্তু ছোট লাল ছাপা ভেঙে টুকরো, ওভারল্যাপ করা লাইন এক বাক্সে, খালি রুল ও ফিল্ডের বর্ডার "শব্দ" হিসেবে বাক্স পায়, Consignment No. মাঝখানে ভাঙা, logo-র অক্ষর বাক্স পায়। Raviraj-এর বাকি ২৬ পাতা ও Amcor চালানো হয়নি — "Raviraj-এ কাজ করে" দাবি করা যাবে না।
- **Universality-র সৎ রায়:** একই PG ফরম্যাট (রঙিন) ✅, B&W ⚠️ আংশিক, ভিন্ন নথি যেমন-আছে ❌, হাতে ঘুরিয়ে ⚠️ আংশিক, "যেকোনো scanned photocopy" ❌ **প্রমাণিত নয়**।

**Track B-র দুটি অতিরিক্ত যাচাই (coordinator-এর নির্দেশে):**
- **H2 নিয়ম (Track D-র 0.58× page-max) — FAILS নতুন পাতায়:** ১৪টি PG পাতায় ০.৫৮ চলে মাত্র **৪টিতে** (Aug p1, p4, p7; May p1)। দুটি উল্টো failure mode — কোনো একক threshold মেটাতে পারে না: (ক) header-box border টেবিলের rule-এর সমান শক্তিশালী (Aug p2/p3/p6, May p2–p5 — ratio ০.৬৯–১.০০); (খ) টেবিলের top rule-ই ফিকে (Aug p5: ০.৫৪২, Aug p8: ০.৪৫৬, May p6: ০.৩৭৬)। মূল কারণ মাপা: rule-এর অন্ধকার/দৈর্ঘ্য template-এর নয়, **প্রতি ভৌত পাতার** ব্যাপার (একই জায়গা y364: Aug p1 run ১৮৬ বনাম Aug p2 run ১৪৭২)। Amcor p1-এ H2 info table-কে বেছে নেয় (test table নয়); Raviraj-এ পাতার কিনারা + "Corporate Office :" — অর্থহীন। প্রস্তাবিত (অপরীক্ষিত) ঠিক: header line ≥১০০০ px ও ≥৬ বাক্স, title band-এর নিচে খোঁজা, band-গুচ্ছের ঘনত্ব।
- **Universal originality audit — সৎ রায়: Track B native DPI কোথাও ধরে রাখেনি।** চারটি নথিই native **৩০০ DPI** (`pdfimages -list` দিয়ে মাপা); কিন্তু pipeline সব ২০০ DPI-তে render করেছে (১.৫× downscale, pixel-সংখ্যা ৪৪%), live-page background JPEG q92 re-encode, clean layer q95 re-encode। v6-র original-bytes background Track B-র পাতায় নেই — deliberate simplification, এখন standing rule-এর বিপরীতে gap হিসেবে রেকর্ড করা। Native ৩০০ DPI-তে আবার চালানো defined follow-up — করা হয়নি, ভানও করা হয়নি। Source PDF-গুলো অক্ষত (read-only)।

### Track C — PDF write-back + DB রেকর্ড — **প্রমাণিত, তারপর native-৩০০ rebuild**

**v1 (৩৩/৩৩ PASS):** ৩ পাতার PDF (p.1 এডিট করা পাতা, p.2 audit copy, p.3 edit certificate) + FreeText "LSE-EDITED v1" mark + `lse-edits.json` ও মূল স্ক্যান verbatim attachment; SQLite DB (`lse_gravora.db`) — deliveries LSE-0001 (Aug) / LSE-0002 (May), `lse_edits` (row label-সহ), hash-chained audit log (genesis prev = ৬৪টি শূন্য; chain-এর সংজ্ঞা এখানে নতুন — core-এর audit টেবিল hash-chained নয়); trigger-এ UPDATE বন্ধ; tamper test-এ chain ভাঙে। Interface: **`LSEPageState v1`** JSON (page_key, source, client/item, `edits[]` — box, old/new text, **row_label দিয়ে পরিচয়**, bold, ink_rgb) → PDF + DB রেকর্ড + `run-summary.json`।

**⚠️ v1-র সৎ সংশোধন (parent-এর স্বাধীন যাচাই + rebuild রিপোর্ট):** v1 রিপোর্টের "এডিট box-এর বাইরে ০ পিক্সেল" দাবিটি **pipeline-এর নিজের ২০০-DPI working image-এর সঙ্গে মাপা ছিল, মূল স্ক্যানের সঙ্গে নয়** — মূল স্ক্যানের সঙ্গে Aug **৪৫৩,২৬৭ px**, May **২৬৬,৩৫৭ px** ভিন্ন ছিল (২০০ DPI-তে মাপা; চোখে প্রায় এক, গড় পার্থক্য ~৬/২৫৫)। v1-র p.1 ২০০ DPI-তে (১৬৫৩×২৩২৩) Flate PNG re-encode — Round 2-র lossless-background মান এডিট করা পাতায় ধরা হয়নি (p.2 audit copy + verbatim attachment-এ মূল অক্ষত ছিল)।

**v2.1 native-৩০০ rebuild (ব্যবহারকারীর সিদ্ধান্ত, ৪০/৪০ PASS — consolidation-এ নিজে আবার চালিয়ে যাচাই: FAILURES: none):**
| যাচাই | August | May |
|---|---|---|
| p.1 ব্যাকগ্রাউন্ড byte == মূল | ✓ JPEG SHA `7b171751…` | ✓ CCITT stream SHA `0500ca66…` |
| TRUE pixel-diff, patch-এর বাইরে (মূল স্ক্যানের সঙ্গে, একই DPI) | **০ excess** — ৪৯৫,২৪৯ px (৫.৭২%) যা decoder baseline-এর সঙ্গে হুবহু সমান (excess ০, missing ০) | **০ px — সত্যিকারের শূন্য** |
| Ink-mask IoU, ২টি এডিট | **১.০০০ / ১.০০০** | **১.০০০ / ১.০০০** |
| "Hard" প্রতিবেশী | ০ px ✓ | ০ px ✓ |
| DB | LSE-0006, SHA `fea9f1b0…` | LSE-0007, SHA `f3151127…` |

- ডিজাইন: মূল byte-ই p.1 ব্যাকগ্রাউন্ড + শুধু এডিট করা শব্দের ছোট patch overlay (Telea inpaint + Grain v2 + DNA render, ৩০০ DPI-তে); ২০০→৩০০ mapping মাপা affine (Aug y-offset +২.২৫ px, May +২.০৭ px — নিছক ×১.৫ নয়); ink bbox ৩০০-DPI মূল ছবিতেই মাপা।
- DB: supersede chain — LSE-0001→0003→0004→0006 (Aug), LSE-0002→0005→0007 (May); **২০টি audit entry, chain অক্ষত** (নিজে DB খুলে যাচাই); trigger অপরিবর্তিত; tamper test chain ভাঙে।
- Rebuild-এ ধরা পড়া bug: v2.0-তে August patch blur হতো (MuPDF float-rounding stretch — ০.০০১ pt rect inset-এ ঠিক, IoU ১.০০০); ১-bit ছবিতে Otsu threshold ০ ফেরে (clamp [৬৪, ২১০])। **অপারেটর ভুল, সৎভাবে রেকর্ড করা:** প্রথম v2.0 রানে LSE-0003-র ফাইল re-run-এ overwrite হয়ে গিয়েছিল — DB row মোছা হয়নি, `lse.delivery.superseded` audit event (LSE-0003 → LSE-0004, কারণসহ) দিয়ে রেকর্ড করা; এরপর থেকে সব rebuild নতুন ফাইলনামে।
- সীমা (v1-র মতোই): এডিট করা শব্দ সামান্য ছোট (Track A-র কাজ); শুধু ২ পাতা × ২ এডিট; `label_ref` NULL (mass-balance লিংক বাকি); certificate ইংরেজি (Helvetica-তে Bengali নেই); SQLCipher নেই; এক পাতায় এক delivery।

### Track D — বাকি জানা fail — **fontfix ৩৫/৩৫, LICENSE VERIFIED**

| বিষয় | আগে | পরে |
|---|---|---|
| fontfix-verify | **৩১/৩৫** (May title ×৩ + PARAMETERS) | **৩৫/৩৫** ✅ |
| Heading flip | — | Aug ১টি ("S.No."), May ৮টি (title ৩ + header ৫) — **০টি false bold**; চোখে যাচাই (header সারি পুরোটাই bold ছাপা); একটা লেবেলের ভুল চোখে ধরা পড়ে ঠিক করা হয়েছে ("STANDARD", column-guess-এর "SPECIFICATION" নয়) |
| Fallback clash | serif B/H/K sans clone-এর মাঝে চোখে ধরা পড়ে | **Sans fallback-এ clash কমে** (মাপা: May BLISTER Sans ০.৫০৮ বনাম Serif ০.৪৫১; Aug BLISTER Serif ০.৫৬২ বনাম Sans ০.৫৫১; typed bold fallback Sans-এ ৫.৫–৬.৯ pp ভালো; ১০০ px render-এ serif B/H/K স্পষ্ট আলাদা, sans মিশে যায়); sans পাতাতেও verify **৩৫/৩৫** |
| vtracer LICENSE | copyright-holder লাইন UNVERIFIED | **verbatim: "Copyright (c) 2024 TSANG, Hao Fung"** — MIT License পাঠ্য (upstream `https://raw.githubusercontent.com/visioncortex/vtracer/master/LICENSE`); identifier **MIT OR Apache-2.0** (upstream Cargo.toml, v1.0.0-alpha.4); **গুরুত্বপূর্ণ: local wheel-এ (vtracer-1.0.0a4.dist-info) কোনো LICENSE ফাইলই নেই** — METADATA-তে শুধু "License: MIT OR Apache-2.0"; repo root-এ `LICENSE-APACHE` নেই (৪০৪ যাচাই করা) |

- **Heading detection (image signal মাত্র, OCR নেই):** H1 — title band-এর গড় ধূসর < ২২০ (Aug ১৯৫.৫ / May ২০৩.৪ বনাম পরের লাইন ২৩৪.৯ / ২৪৩.২); H2 — table top rule > ০.৫৮ × page-max run, তার ঠিক নিচের লাইন header। শুধু bold **যোগ** করে, কখনো কাড়ে না। বাতিল নিয়ম (সংখ্যাসহ): word/line height, line-median stroke ratio, "লাইনে bold শব্দ আছে", rule x-extent, একটিমাত্র absolute run-length threshold।
- **সীমা:** H2-র ০.৫৮ factor মাত্র ২ পাতায় fit করা — Track B-র যাচাইয়ে ১৪ পাতায় ৪/১৪ (§১ Track B দেখুন)। Sans fallback clash **কমায়, দূর করে না** — পুরো সমাধান বড় sans DNA clone set (B, H, K, bold digit)।

### Merge — Track A + Track D একত্রে (v7 পাতা)

- Merge agent staging-এ (`improve/round3/merge/`) দুই patch একত্র করেছে — **কোনো genuine conflict নেই, কোনো track-এর বদল বাদ পড়েনি** (word loop-এ A-র fs/classification + D-র additive heading bold; WORDS-এ `cap_h`/`cls` + `heading`; fallback Sans সরাসরি template edit-এ; matcher v3; fontfix-verify clamp [০.৬০, ১.২৫]; path: walk-up root computation — builders scan-paper/-এ কপি করলেও অপরিবর্তিত চলে)।
- **Consolidation-এ নিজে যাচাই (merge staging-এ + shared tree-তে promote-এর পর):** fontfix-verify **৩৫/৩৫**, verify_round2 **১৮/১৮**, repro PASS, manual_proof **১০/১০**, identity probe **৬/৬** (row label-সহ; "Hard" অক্ষত)।
- **Promote করা হয়েছে (৫টি ফাইল):** `build_page.py`, `build_page_may.py`, `heading.py` (নতুন), `improve/round2/matcher.py` (v3), `improve/fontfix-verify.py` — আর shared v7 পাতা আবার বানানো হয়েছে (Aug ২,৭৪১,৫৭৪ B, ২৯৩ শব্দ, bold ৬৩→৬৪; May ১,০৬৯,০১১ B, ২৭৯ শব্দ, bold ২৭→৩৫)। Merge-only support script promote করা হয়নি।
- সীমা: matcher এখনও Serif fallback দিয়ে DNA-কে score করে, v7 পাতা Sans render করে — ৮টি test শব্দে প্রভাব নেই (fallback অক্ষর নেই), কিন্তু fallback-ওলা typed text-এর ranking মেলে না।

---

## ২. চূড়ান্ত যাচাই টেবিল (consolidation — নিজে চালানো, ২০২৬-১১-০৬)

### ২.১ Live পাতা (v7, shared tree — promote-এর পর)

| যাচাই | ফল | মন্তব্য |
|---|---|---|
| `fontfix-verify.py` | **৩৫/৩৫ PASS** | Round 2-র ৩১/৩৫ থেকে +৪ — May title + PARAMETERS bold ঠিক |
| `verify_round2.py` | **১৮/১৮ PASS** | pixel-diff প্রতি পাতায় ঠিক ২টি blob, Round 2-র একই coordinate |
| `repro.py` | **PASS** | Lot "207/9" `.done`, WIDTH "781.5" `.on`, doubling নেই |
| `manual_proof.py` | **১০/১০ PASS** | signature residue ০, দুই পাতা |
| Identity probe (row label-সহ) | **৬/৬ PASS** | Aug Lot 207/9 [355,619,421,644] লাইন ১১, WIDTH 781.5 [1391,854,1451,873] লাইন ১৬; May Lot 305/7 [347,608,413,633] লাইন ১২, WIDTH 671.5 [1384,860,1445,879] লাইন ১৭; row-01 "Hard" দুই পাতাতেই অক্ষত |
| Matcher v3 (WIDTH) | Aug DNA 0.446 ১ম (tie), May Sans Bold 0.563 ১ম | Track A-র সংখ্যা হুবহু পুনরুৎপাদিত |

### ২.২ PDF write-back (v2.1, native ৩০০ DPI)

| যাচাই | ফল |
|---|---|
| `verify_rebuild_300.py` (আবার চালানো) | **৪০/৪০ PASS, FAILURES: none** |
| TRUE pixel-diff, patch-এর বাইরে (মূল স্ক্যানের সঙ্গে) | May **০ px**; Aug **০ excess** (৪৯৫,২৪৯ px = JPEG decoder baseline হুবহু) |
| Ink IoU, ৪টি এডিট | **১.০০০** সবকটিতে |
| DB read-back + PDF SHA == DB | PASS (LSE-0006 `fea9f1b0…`, LSE-0007 `f3151127…`) |
| Audit hash chain (DB নিজে খুলে যাচাই) | **২০টি entry, chain linked: True**; LSE-0003 SHA mismatch audit event-সহ রেকর্ড করা |
| Tamper test (কপিতে) | chain ভাঙে / `delivery_hash mismatch` ✓ |
| Trigger | audit + delivery UPDATE বন্ধ ✓ |

### ২.৩ Multi-page / multi-document (Track B)

| যাচাই | ফল |
|---|---|
| Aug p2–p8 sample (rows ০১–০৫) | **৩৭/৩৭ সব পাতায়** |
| May p2–p6 sample | **২৯–৩৩/৩৭** (merge systematic) |
| Identity probe, ৩ পাতা (Aug p2, Aug p8, Raviraj p1) | **ALL PASS** (split defect-সহ — এডিট সঠিক শব্দে, ভাঙা অংশ অক্ষত) |
| H2 ০.৫৮ যাচাই, ১৪ PG পাতা | **৪/১৪ PASS** — সাধারণ নিয়ম হিসেবে দাঁড়ায় না |
| Originality audit, ৪টি নথি | native **৩০০ DPI** সবকটিতে; pipeline ধরে রাখে **কোথাও নয়** (২০০ DPI + re-encode) |

---

## ৩. ব্যর্থতা / খোলা বিষয় (এই রাউন্ডে যা মেলেনি)

**কোনো যাচাই-স্যুটে ফেইল বা regression নেই** — সব স্যুট আগের বা ভালো সংখ্যায় সবুজ। নিচেরগুলো খোলা বিষয় — ডিজাইন-সিদ্ধান্ত বা পরের রাউন্ডের কাজ, গোপন ত্রুটি নয়:

1. **DNA WIDTH জয় হয়নি (Track A):** Aug tie (০.০০৩ ব্যবধান), May হার। কারণ DNA clone-এর digit advance ~১০% চওড়া — DNA track-এর metrics-এর কাজ।
2. **H2 ০.৫৮ সাধারণ নয় (Track B):** ১৪ পাতায় ৪/১৪। ৩৫/৩৫ শুধু দুটি p1 পাতায় সত্য — অন্য পাতায় H2 ভুল লাইনকে bold করতে পারে (logo লাইন, Document No. লাইন, signature-এলাকার লাইন)। Round 4-এ গঠনগত guard লাগবে (প্রস্তাব: header line ≥১০০০ px ও ≥৬ বাক্স, title band-এর নিচে খোঁজা, band-গুচ্ছের ঘনত্ব — অপরীক্ষিত)।
3. **Universality প্রমাণিত নয় (Track B):** rotation detection নেই (Raviraj যেমন-আছে ১,০৪৭ ভুয়া শব্দ); ছোট লাল ছাপা, ওভারল্যাপ, রুল/বর্ডার "শব্দ", stamp — সব ভাঙে। শুধু ১টি ভিন্ন নথি, ১টি পাতা মাপা হয়েছে।
4. **Native DPI ধরে রাখা হয়নি live-page pipeline-এ (Track B §১০):** সব ২০০ DPI + re-encode। Standing rule-এর আলোকে এটাই Round 4-র সবচেয়ে বড় কাজ — pipeline-কে native ৩০০ DPI-তে আবার চালানো (re-extract → re-segment → rebuild → probe)।
5. **নতুন defect (Track B):** Aug p5 signature-row leak (১৪ ভুয়া শব্দ — শর্ত component-গোনা থেকে বদলাতে হবে), Aug p8 decimal split, title blob-split ভঙ্গুর (৫/১২ পাতায় ভুল), speck FP, May merge systematic।
6. **এডিট করা শব্দ এখনও সামান্য ছোট** (rendered cap −৮%) — Track A-র sizing ঠিক করেছে শুরুটা, বাকিটা DNA advance-এর কাজ।
7. **Track C-র বাকি:** `label_ref` NULL, Bengali certificate নেই, SQLCipher নেই, এক পাতায় এক delivery, bold/title শব্দের write-back পরীক্ষা হয়নি, শুধু ২ পাতা × ২ এডিট।
8. **কাগজে print calibration হয়নি** — এই VM-এ প্রিন্টার নেই; ফ্যাক্টরির প্রিন্টারে ছাপিয়ে মাপতে হবে (পদ্ধতি `round2/print-calibration.md`-এ)।
9. **DBNet swap স্থগিত, ttfautohint নেই, fallback style clash পুরো দূর হয়নি** (Sans কমায়, দূর করে না)।
10. **v1-র "বাইরে ০ পিক্সেল" দাবির সংশোধন** — v1 রিপোর্টের §০-এর শব্দ এখনও পুরনো মাপের; বর্তমান সত্য rebuild রিপোর্ট §৯ ও এই রিপোর্টের §১ (Track C)।

---

## ৪. এই রাউন্ডে ধরা পড়া নিজের ভুল (সৎ হিসাব)

1. **Track C v1-র "০ পিক্সেল" ভুল মাপের সঙ্গে তুলনা করা হয়েছিল** (২০০-DPI working image, মূল স্ক্যান নয়) — parent-এর স্বাধীন যাচাই ধরেছে; rebuild-এ ঠিক করা হয়েছে (সত্যিকারের pixel-diff মূল স্ক্যানের সঙ্গে)।
2. **Track B-র প্রথম রানে doubling** — builder কপিতে `background-size`-এ scale দুবার লাগানো হয়েছিল (৪১৩×৫৭৯) — ধরা পড়ে ঠিক করা হয়েছে, তিন পাতাই আবার build + probe।
3. **Track D-র প্রথম অনুমান ভুল ছিল** — May [950,755,1079,774] "SPECIFICATION" নয়, চোখে দেখে ঠিক করা হয়েছে: "STANDARD"।
4. **Rebuild-এ অপারেটর ভুল** — LSE-0003-র ফাইল re-run-এ overwrite; audit event দিয়ে রেকর্ড করা (মোছা হয়নি)।
5. **Merge-এ দুটি ছোট bug** — `merge_patch.py`-তে pattern-matching ও import-order ভুল; ধরা পড়ে ঠিক করা হয়েছে।
6. **Track A-র প্রথম eye-clip ভুল row-তে পড়েছিল** (page-top ৭১ ধরা হয়েছিল, আসলে ১৫০) — ভুল ক্লিপ মুছে সঠিক eye2-* ক্লিপ রাখা হয়েছে।

---

## ৫. লাইসেন্স — আপডেটেড চিত্র (কারিগরি গবেষণা, আইনি পরামর্শ নয়)

| বিষয় | অবস্থা |
|---|---|
| **vtracer** | **VERIFIED verbatim** — "Copyright (c) 2024 TSANG, Hao Fung" (upstream LICENSE, MIT পাঠ্য); identifier **MIT OR Apache-2.0** (Cargo.toml); **local wheel-এ LICENSE ফাইল নেই** (METADATA-তে শুধু "License: MIT OR Apache-2.0")। Round 2-র UNVERIFIED সাবধানতা এখন মিটেছে — তবে শুধু কারিগরি পড়া; বিক্রির আগে আইনজীবীর যাচাই এখনো বাধ্যতামূলক |
| **potrace (GPL)** | production ফন্টে নেই (v6/v7 পাতায় vtracer-ফন্ট, byte-identical যাচাইকৃত) |
| **US পেটেন্ট US20150332491A1** | অস্তিত্ব VERIFIED; granted/in-force অবস্থা, claim-এর পরিধি, বাংলাদেশে প্রযোজ্যতা **যাচাই হয়নি — বিক্রির আগে আইনি যাচাই বাধ্যতামূলক** |
| **LaMa / Places2** | ব্যবহার হয়নি — pipeline-এ নেই |
| **MI-GAN** | code + weights MIT VERIFIED, কিন্তু **নেওয়া হয়নি** (NO-GO) |

---

## ৬. এরপর কী (Round 4-এর প্রার্থী)

1. **Native-৩০০-DPI pipeline** — Track B-কে native DPI-তে আবার চালানো (standing rule-এর সবচেয়ে বড় বাকি কাজ)।
2. **DNA digit advance ঠিক করা** — WIDTH-জয়ের মূল বাধা (~১০% চওড়া); B&W-তে DNA-র আচরণ দেখা।
3. **H2 guard** — গঠনগত শর্ত (≥১০০০ px, ≥৬ বাক্স, title band-এর নিচে, band-গুচ্ছ) মেপে বসানো; না হলে H2-কে template-guard-এর পেছনে রাখা।
4. **Rotation/orientation detection** — ভিন্ন নথির প্রথম ব্লকার।
5. **Segmentation শক্ত করা** — sig-row শর্ত (component-গোনা → box-গোনা), title blob-split gap নিয়ম, decimal-split fix, rule/border filter (closed-rectangle + long-rule), B&W merge gap threshold, speck filter।
6. **Sans DNA clone set বাড়ানো** (B, H, K, bold digit) — fallback clash-এর পুরো সমাধান।
7. **বহু-পাতার delivery + `label_ref` mass-balance লিংক + Bengali certificate + SQLCipher** (Track C-র বাকি)।
8. **ttfautohint hinting** — ০.৯৭ fitWidth margin সরানো।
9. **ফ্যাক্টরির প্রিন্টারে print calibration** (M1–M5)।
10. **US পেটেন্টের আইনি যাচাই** — বিক্রির আগে বাধ্যতামূলক।

---

## ৭. ফাইল তালিকা (Round 3)

| ফাইল | বিষয় |
|---|---|
| `improve/round3/track-a/` | Track A — sizing (রিপোর্ট, matcher v3, diagnostics, eye-check) |
| `improve/round3/track-b/` | Track B — coverage (রিপোর্ট, ১২ PG পাতা + Raviraj/Amcor, segs, live পাতা, H2 + originality audit) |
| `improve/round3/track-c/` | Track C — write-back + DB (রিপোর্ট, v1 + v2.1 PDF, `lse_gravora.db`, rebuild রিপোর্ট) |
| `improve/round3/track-d/` | Track D — heading + fallback + LICENSE (রিপোর্ট, `heading.py`, fallback প্রমাণ, LICENSE পাঠ্য) |
| `improve/round3/merge/` | Merge — v7 builder set + suite প্রমাণ (merge রিপোর্ট, `merge_patch.py`) |
| `build_page.py`, `build_page_may.py`, `heading.py` (নতুন) | **v7 shared pipeline** (promote করা হয়েছে) |
| `improve/round2/matcher.py` (v3), `improve/fontfix-verify.py` | v7-তে হালনাগাদ (promote করা হয়েছে) |
| `live-scan-page.html`, `live-scan-page-may.html` | **v7 live পাতা** (shared tree-তে আবার বানানো) |
| `improve/ROUND3-REPORT.md` | **এই রিপোর্ট** |

**নোট:** এই রিপোর্টটি Drive-এ আপলোড করা হয়নি, `REPORT.md` / `REPORT-MAY.md` / `ROUND2-REPORT.md` বদলানো হয়নি — parent-এর নির্দেশ অনুযায়ী সেগুলো parent-এর হাতে।
