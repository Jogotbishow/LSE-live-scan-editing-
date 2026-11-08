# LSE — Round 6 রিপোর্ট (Live-Scan Editing)

**তারিখ:** 2026-11-06 · **স্থিতি: সম্পূর্ণ — পুরো suite সবুজ, কোনো regression নেই।**
**আগের রাউন্ড:** Round 5 (ROUND5-REPORT.md) · **পরের রাউন্ডের প্রার্থী:** §7।

## ১. এক লাইনে ফল

- **Track A:** May-300 WIDTH margin **+0.006 → +0.088** (neighbourhood mean +0.023 → +0.032), Aug-ও **+0.095 → +0.111** — দুই DPI-তেই DNA WIDTH #1, কোনো regression নেই।
- **Track B:** vocabulary gate v3 — **37 merge, 0 false merge**; sample **528 → 522 box / 518 true** (৬টি over-split সব ঠিক); Raviraj p2 misfire ঠিক, মোট **329/394 = 83.5% → 339/394 = 86.0%**।
- **Track C:** May p2/p3 live পাতা বানানো ও যাচাই করা — **43/43**; লেবেল WIDTH সিদ্ধান্তের জন্য মাপা বিকল্প তৈরি — **সিদ্ধান্ত নেওয়া হয়নি, ব্যবহারকারী সিদ্ধান্ত নেবেন** (§4)।
- **Merge:** তিনটি track এক v8 পাতায় মিলেছে; পুরো suite সবুজ (নিচে §5-এর টেবিল)। দুটি staging বাগ ধরা পড়েছে ও ঠিক করা হয়েছে (§5.2) — দুটোই Round 5-এর merge-এর রেখে যাওয়া stale check, আমার merge-এর তৈরি নয়। একটি সৎ ভুল: Round 5-এর Track D PDF-র bytes আর্কাইভ করার আগেই rebuild-এ মুছে গেছে (§5.3)।

## ২. Track A — May-300 margin + bold digit advance (রিপোর্ট: improve/round6/track-a/track-a-report.md)

**সমস্যা ছিল:** Round 5-এ DNA WIDTH 300 DPI-তে জিতলেও May-র margin ছিল মাত্র **+0.006** — noise লাইনের ওপরে বসা জয়। আর bold digit-এর advance consistency খোলা ছিল।

**যা করা হয়েছে (promote-candidate package, staging-এ প্রমাণিত):**
1. **Regular `dna-r6-pg-a.ttf`** (SHA `187b2dfe…`) — per-glyph RSB redistribution, outline অপরিবর্তিত।
2. **Bold `dna-r6-bold-rsb40.ttf`** (SHA `33583cf2…`) — digit RSB 65u → 40u। Bold digit সমস্যা মেপে প্রমাণিত: Aug "EXP202627094" mixed advance +7.9% over box, live_ratio 0.899 বনাম oracle ~0.96–0.98 — regular digit-এর Round 5 সমস্যার হুবহু ছাপ।
3. **FIT_TARGET 0.97 → 0.98** — সবচেয়ে বড় জয় এখান থেকে: May WIDTH 0.552 → 0.613; ৮টি probe word-ই 0.98-এ সমান বা ভালো; 0.975–0.98 plateau, 0.985/1.00 ভেঙে যায়।

**মাপা ফল (merge-এর নিজের re-run, §5):**

| | Aug 300 DPI | May 300 DPI |
|---|---|---|
| WIDTH DNA (rank, margin) | **0.574 (#1, +0.111)** | **0.636 (#1, +0.088)** |
| Lot DNA (rank) | 0.713 (#1) | 0.730 (#1) |
| Page rank DNA Regular | 0.643 (#1) | 0.683 (#1) |
| 200 DPI WIDTH DNA | 0.539 (#1, +0.060) | 0.627 (#1, +0.125) |

- Bold digit: EXP margin −0.004 → **+0.018 (@0.97) / +0.026 (@0.98)**; title সব #1 অপরিবর্তিত।
- **সৎ কথা:** বড় জয়টা fitWidth target 0.98 থেকে (May point +0.061) — এটা mechanism পরিবর্তন, শুধু ফন্ট বদল নয়; pg-a তার ওপরে ছোট কিন্তু ধারাবাহিক বাড়তি (+0.023)। 0.98 margin মাত্র 2% (snap noise) — আসল সমাধান ttfautohint (Round 7)।
- **বাতিল (প্রমাণসহ):** Embolden (May point best 0.585 কিন্তু Aug shape regression 0.695 → 0.601); RSB 37–43 (plateau, সব সমান); bold-rsb30 (EXP-specific, 40 principled); FIT_TARGET 0.985/1.00 (ভাঙে)।
- খোলা: Bold 'X' DNA cmap-এ নেই (Liberation fallback ~30% চওড়া — আলাদা trace-এর কাজ); May bold-digit matcher probe word নেই (May OCR ফাইল নেই)।

## ৩. Track B — Vocabulary gate + Raviraj p2 misfire (রিপোর্ট: improve/round6/track-b/track-b-report.md)

**সমস্যা ছিল:** ৬টি over-split (Aug p8 THICKNESS, May p3 THICKNESS + GRAMMAGE, আরও ৩টি) — Round 5 প্রমাণ করেছিল কোনো gap-based নিয়ম এগুলো ঠিক করতে পারে না। আর Raviraj p2-তে ছোট লাল date-stamp signature-row misfire ঘটিয়ে পাতার নিচের ~26% unsegmented রাখছিল (362 component বাদ)।

**Vocabulary gate (component-width-signature):**
- v1 (43 merge) — 1 false merge (aug-p2 "BY SALES": aug-p5-এর exemplar নিজেই merged box ছিল)।
- v2 (piece-attestation veto) — ব্যর্থ: 31/42 সত্যিকারের fix veto হয়ে গেল (short-signature collision)।
- **v3 (cross-page corroboration: exemplar whole হতে হবে ≥2 DISTINCT পাতায়) — PROMOTED: 37 merge, 0 false merge, সব eye-verified।**
- Sample: **528 → 522 box / 518 true** (৬টি over-split সব ঠিক; 4 speck FP রয়ে গেছে); title **14/14**, H2 **14/14**; মোট শব্দ 4308 → 4271।
- সৎ খরচ: 5টি সত্যিকারের fix মিস (DEPARTMENT + header e-mail ×4 — single-page exemplar মাত্র)।

**Raviraj p2 signature-row misfire — cluster-anchor fix (segment.py v5-300-এ promoted):**
- লম্বা stroke-গুলো y-top অনুযায়ী cluster করা; anchor = সবচেয়ে বড় cluster। p2: sig_y **1829 → 2210** (সঠিক zone), শব্দ **494 → 530**।
- PG পাতা: ঠিক 1টি cluster করে → **14/14 bit-identical, 0 পরিবর্তন**।
- Zone mode বাতিল (প্রমাণসহ): Vehicle/Value/label ফেরে (+51) কিন্তু PG-তে **+28 শব্দ** regression (aug-p5 +9/+10 signature leak)।
- Re-measurement: p2 **73/101 → 83/101 (72.3% → 82.2%)**; p3 অপরিবর্তিত 256/293; **মোট 339/394 = 86.0%** (আগে 83.5%)।
- বাকি: Vehicle/Value ৭ শব্দ (stamp-এর সমান উচ্চতা — y-cutoff আলাদা করতে পারে না); Description অনুচ্ছেদ 2/39 (লাল stamp-এর কালি লাইন জোড়া দিয়ে ৩টি mega-box বানিয়েছে — Round 7 ধারণা: red-ink exclusion)।

## ৪. Track C — May p2/p3 পাতা + লেবেল WIDTH সিদ্ধান্তের প্রস্তুতি (রিপোর্ট: improve/round6/track-c/track-c-report.md)

**May p2/p3 live পাতা (বানানো ও যাচাই করা):**
- `live-scan-page-may-p2-300.html` (2,101,676 B, 313 শব্দ), `live-scan-page-may-p3-300.html` (2,047,532 B, 308 শব্দ)।
- যাচাই **43/43 PASS** (verify_may23_pages.py, merge-এর নিজের re-run): identity probe (row label + box) — p2 Lot [529,909,627,945] 282/5 → **283/7**, WIDTH [2083,1279,2175,1307] 720.0 → **721.5**; p3 Lot [525,909,622,944] 281/5 → **282/7**, WIDTH [2081,1282,2172,1310] 770.0 → **771.5**; "Hard" অক্ষত দুই পাতাতেই; clean background আছে (doubling নেই — ৬টি Lot/WIDTH clip + দুই full page চোখে দেখা)।
- Sample rows 01–05: p2 **37/37** exact; p3-তে 37টি সত্যিকারের শব্দ সব covered, 39 box (২টি extra = আগের over-split, Track B-র কাজ)।
- **আসল বাগ ধরা ও ঠিক করা হয়েছে বানানোর সময়:** v7 May template-এ p1-র visible text hardcode করা ছিল ("পাতা ১", "304/5 → 305/7", "670.0 → 671.5") — p1-এ সঠিক বলে কেউ ধরতে পারেনি; builder এখন প্রতিটি পাতার নিজের মান বসায় (assert-guarded)। Confidence legend-ও ঠিক করা হয়েছে (দুই-detector agreement দাবি করত; p2/p3 tier density-only — DBNet validator নেই ওই পাতাগুলোর জন্য)।
- Regression suite সবুজ: fontfix 45/45, verify_round2_300 18/18, repro PASS, manual 10/10।

**লেবেল WIDTH — সিদ্ধান্তের প্রস্তুতি (সিদ্ধান্ত নেওয়া হয়নি):**
- লেবেলে এখন শুধু p.1-র WIDTH যায় (Round 4 থেকে খোলা): May LBL-0002 "WIDTH (p.1) 671.5 mm" (Lot 305/7), Aug LBL-0005 "WIDTH (p.1) 781.5 mm" (Lot 207/9)।
- মাপা তথ্য — **Aug-এর আসল কেস:** দুই পাতা একই Lot (207/9) কিন্তু WIDTH আলাদা — 781.5 বনাম 776.5, **পার্থক্য 5.0 mm** (COA-র ±0.5 mm band-এর ১০ গুণ)। **May-এর কেস:** প্রতি পাতা আলাদা Lot, WIDTH 671.5 / 721.5 / 771.5 — **বিস্তার 100.0 mm**; ছয় পাতা ধরলে মূল WIDTH 670.0 → 850.0, **বিস্তার 180.0 mm** (p4–p6 মূল মান চোখে দেখে মাপা: 780.0 / 800.0 / 850.0)।
- বিকল্প (নিরপেক্ষভাবে, মাপা পরিণতিসহ — পূর্ণ টেবিল track-c-report.md §3.3-এ): **(a)** p.1 WIDTH শুধু (বর্তমান); **(b1)** প্রতি পাতায় আলাদা লেবেল; **(b2)** এক লেবেলে সব পাতার WIDTH তালিকা; **(c1)** WIDTH range; **(c2)** লেবেলে WIDTH না রাখা; **(c3)** লেবেল পাতা-অনুসরণী (পাতা/প্যাকের)।
- **সিদ্ধান্তের জন্য জরুরি প্রশ্ন (ব্যবহারকারীর কাছে):** লেবেল কি delivery-র (এক delivery = এক লেবেল) নাকি পাতা/প্যাকের? আর May-র মতো multi-lot delivery-তে এক লেবেলে এক Lot+WIDTH থাকা কি আদৌ সত্য হতে পারে? — এই দুই প্রশ্নের উত্তরেই বিকল্প ঠিক হবে। Track C কোনো বিকল্প বেছে নেয়নি; লেবেল ফাইল বা DB বদলানো হয়নি।

## ৫. Merge — তিনটি track এক v8 পাতায়

### ৫.১ কী promote করা হয়েছে
- **ফন্ট:** `improve/round2/dna-prod/dna-clone-regular-600.ttf` ← dna-r6-pg-a.ttf (SHA `187b2dfe…`); `dna-clone-bold-600.ttf` ← dna-r6-bold-rsb40.ttf (SHA `33583cf2…`)। পুরোনো v1d regular + pre-R6 bold `improve/round6/merge/backup/`-এ আছে।
- **FIT_TARGET 0.97 → 0.98** — ৪টি canonical জায়গায়: `improve/round2/matcher.py:89`, `improve/round4/track-b/matcher.py:73`, `build_page.py:453`, `build_page_may.py:424` (দুটি "97%" comment-ও 98%-এ বদলানো হয়েছে)। Track-এর নিজস্ব matcher copy (round3/track-a, round5/track-a, round6/track-a) frozen artifact হিসেবে রাখা হয়েছে — বদলানো হয়নি।
- **পাতা rebuild:** v8 Aug (3,616,571 B, 305 শব্দ — gated count) ও May (2,049,216 B, 309 শব্দ) `build_page300.py` দিয়ে; May p2/p3 Track C builder দিয়ে। সব ৪টি পাতায় JS-এ `* 0.98` আছে বলে যাচাই করা হয়েছে।
- **মনে রাখার মতো গঠন:** `build_page300.py` runtime-এ v7 builder থেকে HTML template নেয়, আর promoted ফন্ট সরাসরি `improve/round2/dna-prod/` থেকে পড়ে — তাই 0.98 পরিবর্তন ও ফন্ট swap স্বয়ংক্রিয়ভাবে rebuild-এ ঢুকেছে।
- **লক্ষ্য করার মতো:** `verify_round2_300.py` চালানোর সময় নিজে `build_page300.py` দিয়ে পাতা rebuild করে — তাই merge-এর শেষ verification pass-এ পাতা আবার লেখা হয়েছে (mtime 16:16) নতুন matcher shortlist (0.643/0.683) embed করে। এটা নকশা অনুযায়ী কাজ, কোনো দুর্ঘটনা নয়।

### ৫.২ Merge-এ ধরা পড়া staging বাগ (দুটোই ঠিক করা হয়েছে, production কোড নয়)
1. **V1 verifier দিয়ে v2 delivery যাচাই — আসল বাগ, Round 5 থেকে ছিল।** `run_track_d1.py`-র pre-flight check সব delivery-তে V1 `verify_delivery` চালাত — কিন্তু v2 multipage delivery-র hash-এ `"pages"` key থাকে, V1 verifier সেটা গোনে না, তাই LSE-0008 সবসময় fail করত। আর count assert `== 20` stale (copy-তে এখন 23 entry — Round 5 merge একই copy-তে staging আবার চালিয়েছিল)। ঠিক করা হয়েছে: v1/v2 আলাদা করা হয় recorded audit detail-এর `'pages'` key দিয়ে (delivery_pages row দিয়ে নয় — v2 migration V1 row-গুলোর জন্যও delivery_pages backfill করে, তাই ওটা দিয়ে আলাদা করা যায় না); count assert এখন শুধু `n_before == n_after` (migration কিছু বদলায় না)। একই stale-scope বাগ `verify_track_d1.py`-তেও ছিল ("all 7 old v1" check-এ LSE-0008 ঢুকে যেত) — ঠিক করা হয়েছে, আর LSE-0008-এর জন্য v2 check যোগ করা হয়েছে (মোট 47 → **48 check**)।
2. **Hardcoded staging count সব জায়গায় stale।** `run_may_multipage.py` (`== 23`, এখন 26), `verify_track_c_r5.py` (Track D PDF-র pinned SHA 0d15605b — Round 6 rebuild-এ SHA এখন 131a9a1b), `sqlcipher_test.py` (23/8/LSE-0009), `keymgmt_proof.py` (35/11/LSE-0012) — সব relative করা হয়েছে (source থেকে মেপে নেওয়া, growth delta দিয়ে যাচাই)। `sqlcipher_test.py`-তে v1-scope বাগও ঠিক করা হয়েছে (একই discriminator) আর "সব v2 hash verify" check যোগ করা হয়েছে (মোট 14 → **15 check**)।

### ৫.৩ সৎ ভুল — Round 5-এর Track D PDF-র bytes হারিয়ে গেছে
Round 6-এর Track D re-run `improve/round4/track-d/lse-edited-aug-p1p2-multipage.pdf` rebuild করার আগে Round 5-এর সংস্করণ (SHA `0d15605b…`) আর্কাইভ করা হয়নি — ফাইলটি এখন Round 6 build (SHA `131a9a1b…`)। Round 5 merge Round 4-এর ফাইলটি ঠিকমতো আর্কাইভ করেছিল (`improve/round5/merge/backup/trackd-r4/`, SHA 7702c57f ✓ — এখনো আছে); আমি সেই নিয়মটা Round 5-এর ফাইলের ক্ষেত্রে মানিনি। ক্ষতি সীমিত: ফাইলটি regenerable staging artifact (একই input থেকে আবার বানানো যায়); **permanent record অক্ষত** — LSE-0008-এর DB row Round 4 SHA নামে, 0d15605b SHA `verify_track_c_r5.py`-র comment-এ সংরক্ষিত আছে, আর নতুন ফাইলের SHA নতুন LSE-0009 DB record-এর সঙ্গে মেলে (verify_track_d1 48/48-এ যাচাই করা)। **পরের রাউন্ডের নিয়ম:** staging output rebuild-এর আগে আর্কাইভ করা বাধ্যতামূলক।

### ৫.৪ Stale matcher.json ফাঁদ (আবার ধরা পড়েছে)
`improve/round4/track-b/matcher.py` চালালে print-এ লেখে "wrote improve/round3/track-a/matcher.json" — কিন্তু আসলে লেখে নিজের directory-তে (`improve/round4/track-b/matcher.json`)। Merge-এর প্রথম পড়ায় আমি ভুল ফাইল (10:46-এর stale, aug 0.446 / may 0.490) পড়ে Track A-র projection-এর সঙ্গে অমিল ভেবেছিলাম; সঠিক ফাইল (15:57, fresh) পড়ে দেখা গেল সংখ্যা হুবহু মিলে (aug 0.539 / may 0.627)। Track A §0-তেও এই ফাঁদ নথিভুক্ত আছে — তবুও আবার পড়তে হয়েছে। Matcher-র print string-টি ভুল; পরের রাউন্ডে ঠিক করা উচিত।

## ৬. চূড়ান্ত যাচাই টেবিল (merge-এর নিজের re-run — সব সংখ্যা এই রাউন্ডে চালিয়ে মাপা)

| যাচাই | ফল | আগের রাউন্ড |
|---|---|---|
| fontfix_verify300.py | **45/45** | 45/45 |
| verify_round2_300.py | **18/18** | 18/18 |
| repro300.py (doubling) | **PASS** | PASS |
| manual_proof300.py | **10/10** | 10/10 |
| Identity probe (Lot+WIDTH+Hard, দুই পাতা) | **12/12** | 12/12 |
| Matcher 300 DPI — WIDTH DNA | Aug **0.574 #1 (+0.111)**, May **0.636 #1 (+0.088)** | Aug +0.095, May +0.006 |
| Matcher 200 DPI — WIDTH DNA | Aug **0.539 #1 (+0.060)**, May **0.627 #1 (+0.125)** | Aug #3, May #3 |
| verify_writeback300.py | **41/41** | 41/41 |
| verify_track_d1.py (Track D staging, LSE-0009 নতুন) | **48/48** | 47/47 (+1 নতুন check) |
| verify_track_c_r5.py (Track C staging, LSE-0013 নতুন) | **74/74** | 74/74 |
| verify_may_multipage.py (May LSE-0010 নতুন) | **59/59** | 59/59 |
| verify_may23_pages.py (May p2/p3) | **43/43** | — (নতুন) |
| sqlcipher_test.py | **15/15** | 14/14 (+1 নতুন check) |
| keymgmt_proof.py | **25/25** | 25/25 |
| Shared Round 3 DB (read-only যাচাই) | **অপরিবর্তিত** — LSE-0001–0007, 20 audit entry, 14 edit, chain OK, ৭টি hash-ই verify | অপরিবর্তিত |

**Eye-check (merge-এর নিজের):** Aug Lot "207/9" পরিষ্কার, WIDTH row-তে "781.5" সঠিক কলামে, row 01 "Hard" অক্ষত; May Lot "305/7", WIDTH "671.5", "Hard" অক্ষত; May p2 Lot "283/7" + WIDTH "721.5", May p3 Lot "282/7" + WIDTH "771.5" — সব পরিষ্কার, কোথাও doubling/ghost নেই। Full edited Aug পাতা চোখে দেখা — title, signature, বাকি সব অপরিবর্তিত।

**নতুন staging delivery (সব staging DB-তে, shared DB নয়):** Track D copy — LSE-0009 (26 audit entry, 9 delivery); Track C staging — LSE-0013, LBL-0006, Lot 207/9, WIDTH 781.5 (43 audit entry, 13 delivery); May copy — LSE-0010, LBL-0003, Lot 305/7, WIDTH 671.5 p.1 only, mechanism test (29 audit entry, 10 delivery)।

## ৭. সৎ সীমা — এখনো যা সম্পূর্ণ নয় (Round 7-এর প্রার্থী)

1. **0.98 margin মাত্র 2% (snap noise)** — আসল সমাধান ttfautohint (Round 2 step-10 follow-up, এখনো হয়নি)।
2. **Over-split-এর 5টি fix মিস** (DEPARTMENT + header e-mail ×4 — single-page exemplar) ও **4 speck FP** রয়ে গেছে; Raviraj-এর নিজের gate vocabulary দরকার।
3. **Raviraj p2/p3 86.0%** (PG 100%) — Vehicle/Value ৭ শব্দ ও Description mega-box বাকি (red-ink exclusion ধারণা)।
4. **May-300 WIDTH margin +0.088** — শক্ত হয়েছে, কিন্তু neighbourhood mean +0.032 এখনো পাতলা; DNA digit advance-এর সূক্ষ্ম কাজ বাকি।
5. **Bold 'X' DNA cmap-এ নেই** (Liberation fallback ~30% চওড়া); May bold-digit matcher probe word নেই।
6. **লেবেল WIDTH সিদ্ধান্ত খোলা** (§4) — ব্যবহারকারীর সিদ্ধান্ত ছাড়া এগোনো যাবে না।
7. **Print calibration** — VM-এ কোনো printer নেই; factory printer-এ `improve/round2/print-calibration.md` অনুযায়ী test-print করতে হবে।
8. **US patent US20150332491A1** — বিক্রির আগে উকিলের যাচাই (আগের মতোই খোলা)।
9. **DBNet swap deferred; Windows DPAPI binding VM-এ প্রমাণ করা যায়নি** (factory PC-তে যাচাইয়ের procedure আছে)।
10. **Standing originality নিয়ম:** Round 6-এ কিছুই downscale/re-encode করা হয়নি — native 300 DPI pipeline অপরিবর্তিত; সব background original JPEG/CCITT bytes থেকে। এই নিয়ম সর্বজনীন — প্রতিটি document type, প্রতিটি DPI, প্রতিটি scan-এ প্রযোজ্য।

## ৮. ফাইল ও অবস্থান

- এই রিপোর্ট: `scan-paper/improve/ROUND6-REPORT.md`।
- Track রিপোর্ট: `improve/round6/track-a/track-a-report.md`, `improve/round6/track-b/track-b-report.md`, `improve/round6/track-c/track-c-report.md`।
- Merge backup: `improve/round6/merge/backup/` (v1d regular + pre-R6 bold ফন্ট, pre-merge v8 পাতা, দুটি matcher, দুটি builder)। Merge clips (identity + May p2/p3): `improve/round6/merge/clips/`।
- Rebuilt পাতা: `live-scan-page-aug-300.html` (SHA `342ab299…`), `live-scan-page-may-300.html` (`4b6b1e4f…`), `live-scan-page-may-p2-300.html` (`7d9f4e1e…`), `live-scan-page-may-p3-300.html` (`78ee2df4…`)।
- Drive-এ কিছু upload করা হয়নি (parent করবেন); REPORT.md / REPORT-MAY.md / ROUND2–5-REPORT.md বদলানো হয়নি।
