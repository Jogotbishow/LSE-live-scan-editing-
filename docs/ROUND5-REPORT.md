# LSE Round 5 — চূড়ান্ত রিপোর্ট (Consolidation + Merge)

**তারিখ:** ২০২৬-১১-০৬ · **স্থিতি: সম্পূর্ণ** — ৩টি ট্র্যাক + মার্জ + স্বাধীন যাচাই শেষ
**প্রযুক্তির নাম: LSE — Live-Scan Editing**
**ফাইল:** `scan-paper/improve/ROUND5-REPORT.md` · **সূত্র:** `improve/round5/`-এর ৩টি ট্র্যাক-রিপোর্ট + মার্জে নিজে চালানো যাচাই

> ⚠️ **আইনি দাবিত্যাগ:** এই রিপোর্ট কারিগরি গবেষণা, আইনি পরামর্শ নয়। লাইসেন্স/পেটেন্টের অংশ পড়ে কোনো সিদ্ধান্ত নেওয়ার আগে একজন আইনজীবীর সঙ্গে পরামর্শ বাধ্যতামূলক।

> **স্থায়ী নিয়ম (ব্যবহারকারী, ২০২৬-১১-০৬ — UNIVERSAL):** নথির FULL originality রক্ষা করতে হবে — মূল নথি যে DPI-তে আছে, সেই DPI-তেই কাজ করতে হবে; কখনো downscale নয়, ব্যাকগ্রাউন্ড কখনো re-encode নয়, resolution কখনো বদল নয়। **এটি সব ধরনের নথি, সব DPI, সব স্ক্যানের ক্ষেত্রে প্রযোজ্য, শুধু PG COA নয়।** কোনো ধাপে আসল কারণে originality রক্ষা করা না গেলে চুপচাপ মান কমানো যাবে না — সৎভাবে জানাতে হবে।

---

## ০. এক লাইনে

Round 5-এর ৩টি ট্র্যাক + মার্জ — সব মাপা হয়েছে, আর consolidation-এ পুরো স্যুট **নিজে আবার চালিয়ে** নিশ্চিত করা হয়েছে: **DNA WIDTH-এ ৩০০ DPI-তে দুই পাতাতেই জেতে (Aug 0.585, May 0.552)**; বাংলা সনদপত্র মার্জ করা PDF-র p5-এ (LSE-0012, ৭৪/৭৪); SQLCipher চাবি-ব্যবস্থাপনা নকশা + প্রমাণ (২৫/২৫); May ৩-পাতার delivery যাচাই (৫৯/৫৯); fontfix_verify300 **৪৫/৪৫**, verify_round2_300 **১৮/১৮**, write-back **৪১/৪১**, track-d **৪৭/৪৭** — কোনো regression নেই। তবে তিনটি সৎ কথা: **(১)** May-৩০০ point margin মাত্র +0.006 (noise-সীমায় — neighbourhood mean-ই জয়টিকে ধরে রাখে); **(২)** over-split-এর কোনো gap-ভিত্তিক ঠিক নেই — প্রমাণসহ নেতিবাচক ফল, vocabulary gate Round 6-এর কাজ; **(৩)** Raviraj p2-র নিচের ২৬% segment-ই হয়নি (signature-row misfire) — ৮৩.৫% বনাম PG-র ১০০%।

---

## ১. Track A — DNA WIDTH-জয় ৩০০ DPI-তে ✅ (মার্জ করা)

### ১.১ মূল কারণ — মাপা, অনুমান নয়

**DNA clone-এর digit advance এখনো ৭–৯% বেশি চওড়া।** 300 DPI-তে fs0-এ "780.0"-র advance 97.9 px (box 90 px, +8.8%), "670.0"-র 97.1 px (box 91 px, +6.7%)। Live page-র fitWidth তাই DNA-কে 0.892× / 0.909×-এ shrink করে — DNA-র oracle size (0.97×) থেকে 0.06–0.08 নিচে। Serif/Sans Bold-এর advance box-এর প্রায় সমান (90.0 px), তাই তারা 0.97×–0.98×-এ থাকে। **Shape-এ DNA-র কোনো দোষ নেই — size-ই দোষী, আর size advance-ই ঠিক করে।** DNA-র oracle Aug-এ সবার সেরা (0.828), May-এ ২য় (0.716); plain IoU @fs0 ও IoU_vec-ও DNA সেরা দুই পাতাতেই — শুধু IoU_live-এ DNA হারে, অর্থাৎ দোষ fitWidth shrink-এ।

- **বাড়তি advance-এর উৎস পাতা-ভেদে উল্টো:** Aug-এ DNA ink +5 px চওড়া (gap ঠিক), May-এ DNA ink ঠিক (gap +4.2 px চওড়া) — Aug colour JPEG বনাম May B&W CCITT thresholding; May median stroke 7.0 px বনাম Aug 5.0 px (300 DPI)। একটাই ফন্ট দুই পাতার metric-কে নিখুঁত মেলাতে পারে না — RSB কাটাই compromise।
- **200-DPI "জয়" metric noise-এর ভেতরে ছিল:** 200 DPI-তে IoU-vs-size curve-এ পাশাপাশি 1% step-এ jump ±0.13–0.22 (সব ফন্টে), অথচ DNA-র জয়ের margin ছিল মাত্র +0.039 / +0.046। 300 DPI-তে curve smooth (±0.04–0.14) — তাই 300 DPI-ই বিশ্বাসযোগ্য মাপ। আরও: 200-DPI cap_h কম মাপা হয় (May 18 বনাম 28/1.5 = 18.67 px — downscale blur + Otsu), ফলে live_ratio-তে ±3% cap_h noise। PIL float-size truncation বাতিল (getlength 85.61→86.08→87.28)।
- **Baseline-এর neighbourhood mean আগেই চারটি WIDTH case-এ প্রতিদ্বন্দ্বীর চেয়ে বেশি ছিল** — 300-DPI point হারটা ছিল DNA নিজের curve-এর মাঝামাঝি point-এ পড়া আর Serif Bold-এর peak-এ পড়ার কাকতাল। তাই point-value-এর পাশাপাশি ৭-point neighbourhood mean (fs_live × 0.97–1.03) রিপোর্ট করাই সৎ পদ্ধতি।

### ১.২ Variant shootout — ৮টি variant, একটিই দুই পাতায় জেতে

| Variant | 300 Aug | 300 May | 200 Aug | 200 May |
|---|---|---|---|---|
| baseline (RSB 75u) | 0.449 (২য়, −0.041) | 0.498 (৩য়, −0.048) | 0.482 (১ম, +0.039) | 0.609 (১ম, +0.046) |
| v1c-rsb50 | 0.495 (+0.005) ১ম | 0.541 (−0.005) ২য় | **0.637 (+0.194) ১ম** | 0.600 (+0.037) ১ম |
| v1e-rsb45 | 0.579 (+0.089) ১ম | 0.546 (+0.000, tie) ১ম | 0.434 (−0.009) ২য় | 0.572 (+0.009) ১ম |
| **v1d-rsb40 ★** | **0.585 (+0.095) ১ম** | **0.552 (+0.006) ১ম** | 0.426 (−0.017) ৩য় | 0.509 (−0.054) ৩য় |
| v1f-rsb35 | 0.584 (+0.094) ১ম | 0.528 (−0.018) ৩য় | 0.469 (+0.026) ১ম | 0.509 (−0.054) ৩য় |

Neighbourhood mean (৭ point): v1d 300 Aug 0.514 (Serif Bold 0.438), 300 May 0.560 (Sans Bold 0.537) — point-জয়কে সমর্থন করে। Condense variant বাতিল (Round 4-র V2 সিদ্ধান্ত 300 DPI-তেও ধরে — May single-glyph IoU 0.687 → 0.659/0.647, আসল shape regression)। RSB-only variant-গুলোতে single-glyph IoU baseline-এর সঙ্গে হুবহু এক (0.695 / 0.687) — **shape-এ শূন্য আপস**। Lot-ও ভালো হয় v1d-তে (Aug 0.590→0.619, May 0.539→0.688); titles অপরিবর্তিত (bold ছোঁয়া হয়নি); page rank DNA Regular #1 দুই 300-DPI পাতাতেই (0.602 / 0.620)।

### ১.৩ সিদ্ধান্ত (coordinator): v1d promote — trade-off সৎভাবে লেখা

**v1d-ই একমাত্র variant যা 300-DPI WIDTH দুই পাতাতেই point-value-এ জেতে** — আর 300 DPI-ই আসল ডেলিভারেবল (v8 পাতা canonical; v7 200-DPI পাতা frozen artifact, আর 200-DPI matcher-এ ±3% cap_h noise)। v1c-rsb50 বিকল্প ছিল (200 DPI-তে দুই পাতাতেই জেতে, 300 DPI-তে Aug +0.005 / May −0.005 — লক্ষ্য পূরণ হয় না)। **সৎ সীমা:** May-300 point margin মাত্র +0.006 — জয়টা point + neighbourhood mean (+0.023) দুটোতেই আছে, কিন্তু point একা নিরঙ্কুশ প্রমাণ নয়; Aug-এর +0.095-ই শক্ত margin। 200-DPI WIDTH point ranking regress করে (১ম/১ম → ৩য়/৩য়) — frozen artifact + noisy metric বলে মেনে নেওয়া হয়েছে, লুকানো হয়নি। Bold ফন্ট ছোঁয়া হয়নি (bold digit advance এখনো ink+65u) — consistency item, Round 6-এ।

---

## ২. Track B — Segmentation বাকি + যাচাইয়ের ফাঁক ✅ (৩টি অংশ)

### ২.১ Over-split — নেতিবাচক ফল, প্রমাণসহ ❌

**Round 4-এর সংশোধন: over-split ৩টি নয়, ৬টি** — Aug p7 THICKNESS, Aug p8 THICKNESS, May p3 THICKNESS, May p3 GRAMMAGE, May p4 GRAMMAGE, May p6 THICKNESS (সব চোখে দেখে যাচাই)। Per-page নমুনা: **৫২৮টি বাক্স বনাম ৫১৮টি সত্য শব্দ = ১০টি অতিরিক্ত** (৬ over-split + ৪ speck FP)। ভাঙন হয় v3 wide-word split-এ (TOP-2, mult 2.0) — প্রতিটি over-split-এ ঠিক একটি qualifying gap, ratio blob-এর median gap-এর 2.0–2.17×। নমুনার বাইরেও ভাঙছে: DEPARTMENT, PARAMETERS, STANDARD, "nvestigation"।

- **R-COMB বাতিল** (আসল "BY SALES" আটকাবে, ratio 1.83)।
- **R-LINE বাস্তবায়ন করে বাতিল:** ৬টি over-split + DEPARTMENT/PARAMETERS/STANDARD ঠিক হয়, কিন্তু regression আসে — Aug p1 title "ANALYTICAL TEST" এক বাক্সে, Aug p8 title-এ overlapping duplicate বাক্স, May p3/p4-এ "BY SALES" এক বাক্সে; মার্জিন সর্বত্র ০–১px। **প্রমোট করা হয়নি।**
- **চূড়ান্ত প্রমাণ — gap দিয়ে আলাদা করা যায় না:** "BY SALES" আসল word-gap ratio 1.83× < THICKNESS অক্ষর-gap 2.0–2.17×; May p3 "BY SALES" gap 9px < তার লাইনের ন্যূনতম আসল gap 10px; Aug p7 title-র আসল word-gap (8px, ঠিক 2.0×) = THICKNESS-এর অক্ষর-gap ratio। Absolute gap, relative ratio, line-min, টুকরোর আকার, mean advance — সব overlap করে। একমাত্র নির্ভরযোগ্য পার্থক্য অক্ষরগুলো নিজে (lexicon)।
- **সুপারিশ (যাচাই করা ধারণা, বাস্তবায়ন হয়নি):** two-pass vocabulary gate — component-width signature (±3px, n_comp ±1) আসল exemplar মেলে আর ভুলটিকে বাতিল করে (THICKNESS/GRAMMAGE/DEPARTMENT-এ প্রমাণিত; PARAMETERS-এ n_comp ±1 tolerance লাগবে)। **Round 6-এর কাজ।** আপাতত over-split একটি documented known limitation — শব্দগুলো পুরোপুরি covered ও editable, শুধু দুই টুকরোয় এডিট করতে হয়।

### ২.২ Raviraj p2/p3 হাতে-গোনা যাচাই ✅ — বড় ত্রুটি পাওয়া গেছে

| | TRUE | correct | accuracy |
|---|---|---|---|
| Raviraj p2 (N3 বাদে) | 101 | 73 | **72.3%** (sig_y region বাদে 86.9%) |
| Raviraj p3 | 293 | 256 | **87.4%** |
| **মোট** | **394** | **329** | **83.5%** (split ২৯, merge ৫, miss ২৫ — ১৭টি sig_y থেকে — FP ২১) |

- 🚨 **p2 signature-row misfire:** seg-এ cy > 1818-এর কোনো শব্দ নেই (sig_y=1829, পাতার উচ্চতা 2480) — পাতার নিচের **~২৬% একদম segment হয়নি** (Vehicle No. NL01AG9964, Value USD $58802.89, চার্জ, FREIGHT PREPAID, checkbox, CARRIER NAME, Signature + stamp — **৩৬২টি component বাদ**। ট্রিগার: Description cell-এর ভিতরে ছোট লাল তারিখের স্ট্যাম্প ("DTD 08/08/26") — স্বাক্ষর নয়। সঠিক sig_y হতো ~2210। **ঠিক করার দিক:** exclusion শুধু signature/stamp **zone**-টুকু ঢাকবে, প্রথম tall stroke-এর নিচের সবকিছু নয়। Round 4-র "p2: 494 শব্দ" তাই পুরো পাতার সংখ্যা নয় — উপরের ৭৪%-এর সংখ্যা।
- অন্য ত্রুটি: দশমিক সংখ্যা বিন্দুতে ভাঙে (p3-এ "10138.43"→২, "5.80"→২); stamp/logo graphics বাক্স হয়; "RAVIRAJ FOILS LIMITED" p3 header-এ হারিয়েছে কিন্তু অন্যত্র বাক্স হয়েছে; তারিখ ভাঙা অসামঞ্জস্যপূর্ণ ("30/06/26" ১ বাক্স বনাম "07/08/2026" ৩ বাক্স); ছোট লাল ছাপা ভেঙে চুরমার (blob-split ~২০% বনাম PG p1-এর ~১০%)। PG-র 518/518 নমুনার চেয়ে অনেক খারাপ — consignment note / invoice কঠিন ডকুমেন্ট।

### ২.৩ May multi-page delivery ✅ 59/59 PASS

- **আগে জানা জরুরি:** May-র প্রতিটি পাতা **আলাদা lot** (p1 304/5, p2 282/5, p3 281/5, p4 280/5, p5 279/5, p6 269/5 — চোখে দেখে নিশ্চিত)। তাই আসল single-lot May multi-page delivery এই ডকুমেন্ট দিয়ে বানানোই যায় না। **LSE-0009 একটি MECHANISM TEST** (state file, certificate, label footnote, DB audit_extra, রিপোর্ট — সব জায়গায় স্পষ্ট লেখা)।
- **Delivery LSE-0009** (id `LSE-DEL-64c5852094734c19817b79c2da2bf87f`), label **LBL-0002** (305/7, 671.5)। মার্জ করা PDF ৭ পাতা (৩ edited + ৩ audit + ১ cert), 574,709 B, SHA `5cbc8673…`। ৬টি এডিট identity-probe-সহ (p2 Lot 282/5→283/7, WIDTH 720.0→721.5; p3 Lot 281/5→282/7, WIDTH 770.0→771.5; "Hard" অক্ষত, 0px)। **TRUE pixel-diff vs মূল স্ক্যান = ০** তিন পাতাতেই (CCITT-তে JPEG decoder floor নেই); ink IoU 1.000 ছয়টিতেই; hash chain ২৬ entry; ৪টি UPDATE trigger block; ৩টি tamper test chain/hash ভাঙে। **যাচাই 59/59 PASS**, ক্লিপ চোখে দেখা পরিষ্কার (doubling/ghost নেই)।
- যাচাইয়ের সময় ধরা ২টি বাগ (ঠিক করা হয়েছে): (ক) certificate পাতা ফাঁকা ছিল — `insert_textbox` text না ফিটলে নীরবে কিছুই insert করে না (৫৪ লাইন 10pt-এ 7.43pt বেশি লাগছিল); 9.5pt-এ ঠিক, cert এখন 2,796 অক্ষর। (খ) "পুরনো delivery" চেক ভুল ছিল — v1 verifier v2 delivery-তে mismatch দেয় (চেকের ভুল, regression নয়)।
- **সীমা:** May p2/p3-র live HTML পাতা বানানো হয়নি (edit state verified seg + চোখে দেখা মান থেকে); আসল single-lot May delivery-র জন্য same-lot ডকুমেন্ট দরকার।

---

## ৩. Track C — বাংলা সনদপত্র + SQLCipher চাবি-ব্যবস্থাপনা ✅

### ৩.১ বাংলা সনদপত্র মার্জ করা PDF-র p5-এ ✅ 74/74 PASS

**চূড়ান্ত delivery LSE-0012** (label LBL-0005 — মার্জে নতুন ফন্টে পুনর্নির্মাণ; LSE-0011 supersede করা, মোছা হয়নি), মার্জ করা PDF ৫ পাতা, 2,118,151 B, SHA `7764f386…`। p5 বাংলা সনদপত্র — Chromium/HarfBuzz-এ রেন্ডার (ReportLab বাংলা যুক্তাক্ষর গঠন করে না), vector text-এ বসানো, p1-র সমান আকার (595.92×836.40 pt)। **যাচাই 74/74 PASS** (`verify_track_c_r5.py`): p1/p2 ব্যাকগ্রাউন্ড JPEG byte-identical; TRUE pixel-diff = decoder baseline হুবহু (excess ০); "Hard" ০ px; ink IoU **1.000 চারটিতেই**; embedded মূল স্ক্যান byte-identical; PDF SHA == DB; chain **৩৯টি entry**; ১২টি delivery; trigger block; tamper test chain/hash ভাঙে।

- **চোখে দেখা (2x):** যুক্তাক্ষর লাইন ঠিকভাবে গঠিত — ক্ষতি, জ্ঞান, বিস্তার, স্পষ্ট, রাষ্ট্র, স্মৃতি, শ্রমিক, চন্দ্র, উত্তর, অন্তর, স্বাস্থ্য, প্রক্রিয়া, সংযুক্ত, প্রশ্ন, লক্ষ্য, অক্ষর — কোনো ভাঙা অক্ষর বা tofu নেই; টেবিলে বাংলা সংখ্যা ঠিক (২০৬/৭ → ২০৭/৯, ৭৮০.০ → ৭৮১.৫, ৭৭৫.০ → ৭৭৬.৫); পাতা পুরোটা সাদা।
- **চোখে ধরা ২টি আসল ত্রুটি (ঠিক করা হয়েছে):** (১) প্রথম build-এ সনদপত্রের নিচে ~১২ mm ধূসর ডোরা (৯৩–৯৫% উচ্চতায় ৮৯% ধূসর) — কারণ body background `#f3f1ec` (Chromium print-pagination); `#fff`-এ ঠিক, এখন ০.০০ ধূসর। (২) supersede লাইনের ভুল কথা ("আগেরটি ইংরেজি ছিল" — LSE-0009 → LSE-0010-এ ভুল) — লাইনটি নিরপেক্ষ করা হয়েছে। প্রতিটি পুনর্নির্মাণ নতুন delivery (LSE-0009 → 0010 → 0011 → 0012) — পুরনো delivery মোছা হয়নি।
- **Text-extraction-এর সীমা (জানা):** Chromium কিছু বাংলা স্বরচিহ্ন দুবার লেখে (জ্ঞান → "জ্ঞাান") — তাই যাচাইয়ে শুধু extraction-এ পরিষ্কার শব্দগুলো গেট করা হয়েছে; **পূর্ণ যুক্তাক্ষর লাইনের প্রমাণ চোখে দেখা**।

### ৩.২ SQLCipher চাবি-ব্যবস্থাপনা ✅ নকশা + প্রমাণ 25/25 PASS

**নকশা** (`key-management-design.md`): মাস্টার চাবি ৩২ বাইট random (যন্ত্রের তৈরি, মানুষের টাইপ করা নয়) → থাকে **চাবি-ভল্টে** (আরেকটি SQLCipher DB) → ভল্ট খোলে অপারেটরের **পাসফ্রেজ** দিয়ে (PBKDF2-HMAC-SHA256, ২০০,০০০ বার, salt sidecar JSON-এ) → উৎপাদনে পাসফ্রেজ থাকে **Windows Credential Manager-এ (DPAPI)**। SQLCipher 4 সেটিংস পিন করা (kdf_iter 256000, HMAC-SHA512)। ঘূর্ণন: `PRAGMA rekey` (পুরনো চাবি ৩০ দিন `previous` হিসেবে ভল্টে); ব্যাকআপ: এনক্রিপ্ট করা DB + ভল্টের কপি (USB) + **কাগজে ছাপা পুনরুদ্ধারের কাগজ** (সেফে); চাবি + ভল্ট + কাগজ তিনটিই হারালে ডাটা চিরতরে যাবে — সৎভাবে লেখা আছে। সম্পূর্ণ অফলাইন: কোনো সার্ভার/KMS/ইন্টারনেট নেই; প্রতি PC-র নিজের চাবি।

**প্রমাণ** (`keymgmt_proof.py`, SQLCipher 4.20.0 — **২৫/২৫ PASS**): ভল্ট শুধু সঠিক পাসফ্রেজে খোলে; এনক্রিপ্ট করা DB শুধু ভল্টের চাবিতে খোলে (plain sqlite3 / চাবি ছাড়া / ভুল চাবি → "file is not a database"); chain (৩৫টি entry) + সব hash মেলে; TEST delivery লেখা যায় (৩৫ → ৩৭, chain মেলে); backup/restore round-trip byte-identical; rotation — পুরনো চাবি খোলে না, নতুন চাবি খোলে, chain ৩৫টি অপরিবর্তিত; byte বদলানো কপি পড়তে গেলে ধরা পড়ে (HMAC)। এনক্রিপ্ট করা DB 147,456 B = plaintext আকার। **শেখা বিষয়:** tamper পড়ার সময় ধরা পড়ে, খোলার আগেই নয় (মাঝের byte বদলে `SELECT count(*)` খুলেছিল — সঠিক পরীক্ষা পাতা ১-এ byte বদলানো + পুরো chain পড়া)।

**সীমা:** Windows Credential Manager / DPAPI এই Linux VM-এ প্রমাণ করা হয়নি — উৎপাদনে Windows-এ বাইন্ডিং লিখে পরীক্ষা বাধ্যতামূলক; পাসফ্রেজের শক্তি অপারেটরের ওপর নির্ভরশীল; একাধিক অপারেটর / HSM / TPM ডিজাইন হয়নি।

---

## ৪. মার্জ — coordinator নিজে যা করল

1. **DNA ফন্ট promote:** Round 4-র regular ফন্ট ব্যাকআপ (`merge/backup/dna-clone-regular-600-r4.ttf`, SHA `724b5d85…`) → `dna-r5-v1d-rsb40.ttf` (SHA `b3e61ec3…`, 11,520 B) দিয়ে বদলানো; bold ফন্ট অপরিবর্তিত। v8 পাতা `build_page300.py`-তে আবার বানানো (Aug 3,616,758 B, May 2,049,587 B)।
2. **Write-back staging পুনর্নির্মাণ (নতুন ফন্টে):** Round 4-র staging DB + PDF ব্যাকআপ (`merge/backup/writeback-r4/`) → শেয়ার্ড Round 3 DB থেকে fresh copy → LSE-0008/0009 আবার বানানো → যাচাই **41/41, FAILURES: none**।
3. **Track D staging পুনর্নির্মাণ (নতুন ফন্টে):** পুরনো copy DB + merged PDF ব্যাকআপ (`merge/backup/trackd-r4/`) → fresh copy → LSE-0008 / LBL-0001 আবার বানানো → যাচাই **47/47, FAILURES: none**।
4. **Track C delivery পুনর্নির্মাণ (নতুন ফন্টে):** driver আবার চালানো → **LSE-0012** (LBL-0005) LSE-0011-কে supersede করে → যাচাই **74/74, FAILURES: none**। Verifier-এর একটি stale চেক ঠিক করা হয়েছে: "Round 4 merged PDF unchanged" — merge-ই ফাইলটি ইচ্ছাকৃতভাবে পুনর্নির্মাণ করেছে (পুরনো SHA `7702c57f…` ব্যাকআপে আছে), তাই চেকটি এখন পুনর্নির্মিত ফাইলের SHA (`0d15605b…`) মেলায়; আর LSE-0008-র DB রেকর্ড এখনো মূল Round 4 SHA-ই নামে (immutable ইতিহাস) — দুটি আলাদা constant-এ লেখা হয়েছে।
5. **May delivery পুনর্নির্মাণ (নতুন ফন্টে):** পুরনো May staging ব্যাকআপ (`merge/backup/may-r5/`) → পুনর্নির্মিত Track D copy DB থেকে fresh copy → **LSE-0009** / LBL-0002 আবার বানানো (mechanism-test নোট অপরিবর্তিত) → যাচাই **59/59, FAILURES: none**।
6. **CCITT dimension patch মার্জ (শেয়ার্ড builder-এ):** `lse_writeback_300.py`-র `_add_ccitt_background` May p.1-র 2477×3473 hardcode করত — এখন `spec["native_px"]` থেকে পড়ে (Track B-র `may_specs.py` monkey-patch-এর একই যুক্তি; ব্যাকআপ `merge/backup/lse_writeback_300-pre-r5merge.py`)। May p1-র জন্য no-op (native_px ঠিক (2477, 3473)), may2 (2483×3473) ও may3 (2477×3467)-র জন্য ভুল ঘোষণা ঠিক হয়। মার্জের পর চারটি verifier আবার চালানো হয়েছে — সব PASS (নিচে §৫)।
7. **শেয়ার্ড Round 3 DB অটুট:** LSE-0001–0007, ২০টি audit entry, chain linked (নিজে খুলে যাচাই)। v7 (200-DPI) পাতা অটুট। `REPORT.md` / `REPORT-MAY.md` / `ROUND2/3/4-REPORT.md` ছোঁয়া হয়নি। Drive-এ কিছু আপলোড করা হয়নি।

---

## ৫. চূড়ান্ত যাচাই তালিকা (সব আমি নিজে চালিয়েছি — মার্জের পর)

| চেক | ফল |
|---|---|
| fontfix_verify300.py (v8 পাতা, v1d ফন্ট) | **45/45 PASS** |
| verify_round2_300.py | **18/18 PASS** |
| repro300.py (doubling) | **PASS** |
| manual_proof300.py | **10/10 PASS** |
| Matcher 300 DPI (promoted ফন্ট) | **DNA WIDTH জেতে দুই পাতাতেই** — Aug 0.585 (#1), May 0.552 (#1); Lot #1 দুই পাতাতেই; Title #1 (৪/৪); page rank DNA Regular #1 (0.602 / 0.620) |
| Matcher 200 DPI (promoted ফন্ট) | DNA WIDTH #3 দুই পাতাতেই (Aug 0.426, May 0.509) — §১.৩-এর রেকর্ড করা trade-off |
| verify_writeback300.py (মার্জ staging DB) | **41/41 PASS, FAILURES: none** |
| verify_track_d1.py (multipage + label_ref) | **47/47 PASS, FAILURES: none** |
| verify_track_c_r5.py (Bengali cert, LSE-0012) | **74/74 PASS, FAILURES: none** |
| verify_may_multipage.py (May LSE-0009) | **59/59 PASS, FAILURES: none** |
| sqlcipher_test.py (encrypted DB) | **14/14 PASS, FAILURES: none** |
| keymgmt_proof.py (Track C, SQLCipher 4.20.0) | **25/25 PASS** (Track C-র প্রমাণ; মার্জে DB/ভল্ট ছোঁয়া হয়নি) |
| Identity probe (row label + box, rebuilt v8) | **PASS দুই পাতাতেই** — Aug Lot "207/9" [533,930,631,966], WIDTH "781.5" [2088,1282,2178,1310]; May Lot "305/7" [521,913,619,950], WIDTH "671.5" [2078,1290,2169,1318]; "Hard" অক্ষত দুই পাতাতেই |
| চোখে দেখা (৪টি ক্লিপ, rebuilt v8) | **PASS** — Lot/WIDTH পরিষ্কার, কোনো doubling/ghost নেই; clean background লেগেছে |
| শেয়ার্ড Round 3 DB | **২০টি entry, chain linked**, LSE-0001–0007 অটুট |

---

## ৬. সৎ সীমা — যা এখনও সম্পূর্ণ নয় (Round 6 প্রার্থী)

1. **May-300 WIDTH point margin পাতলা (+0.006)** — জয়টা point + neighbourhood mean (+0.023) দুটোতেই আছে, কিন্তু point একা নিরঙ্কুশ প্রমাণ নয়। Matcher-এ neighbourhood mean যোগ করার প্রস্তাব (Track A §৫.৫)।
2. **Over-split ঠিক হয়নি** — কোনো gap-ভিত্তিক নিয়মে হয় না (প্রমাণিত)। Vocabulary gate (component-width signature ±3px, n_comp ±1) বাস্তবায়ন + ১৪ পাতা + Raviraj-এ পূর্ণ যাচাই Round 6-এর কাজ। নমুনায় ৬টি + নমুনার বাইরে DEPARTMENT/PARAMETERS/STANDARD/"nvestigation"।
3. **Raviraj p2 signature-row misfire** — নিচের ২৬% unsegmented (৩৬২ comp); exclusion zone-ভিত্তিক fix দরকার। Raviraj সম্মিলিত ৮৩.৫% বনাম PG ১০০% — দশমিক ভাঙা, stamp/logo FP, তারিখ অসামঞ্জস্য এখনো খোলা।
4. **May p2/p3-র live HTML পাতা বানানো হয়নি** (write-back seg box + affine-ই ব্যবহার করে); আসল single-lot May delivery-র জন্য same-lot ডকুমেন্ট দরকার।
5. **লেবেলে শুধু p1-র WIDTH** (781.5 / 671.5) — কোন পাতার মান লেবেলে যাবে, সেটা product-সিদ্ধান্ত (Round 4 থেকেই খোলা)।
6. **Windows DPAPI বাইন্ডিং প্রমাণ হয়নি** (Linux VM) — উৎপাদনে Windows-এ লিখে পরীক্ষা বাধ্যতামূলক; একাধিক অপারেটর / HSM / TPM ডিজাইন হয়নি।
7. **Bold digit advance consistency** (ink+65u, অপরিবর্তিত) — bold WIDTH শব্দের matcher coverage নেই।
8. **Print calibration** — VM-এ প্রিন্টার নেই; কারখানার প্রিন্টারে করতে হবে (পদ্ধতি `improve/round2/print-calibration.md`-এ)।
9. **US পেটেন্ট US20150332491A1** — বিক্রির আগে আইনজীবীর যাচাই লাগবে (আমার কাজ নয়)।
10. **DBNet swap** এখনও deferred (classical primary)।
11. **200-DPI WIDTH ranking regression** (v1d) — frozen v7 artifact + noisy metric বলে মেনে নেওয়া হয়েছে (§১.৩)।

---

## ৭. যা বদলেছে (শেয়ার্ড ট্রি) — প্রমোট তালিকা

**বদলানো ফাইল (ব্যাকআপ `improve/round5/merge/backup/`-এ):**
- `improve/round2/dna-prod/dna-clone-regular-600.ttf` — v1d RSB 40u (SHA `b3e61ec3…`; পুরনো `merge/backup/dna-clone-regular-600-r4.ttf`, SHA `724b5d85…`); bold ফন্ট অপরিবর্তিত
- `live-scan-page-aug-300.html` (3,616,758 B), `live-scan-page-may-300.html` (2,049,587 B) — v1d ফন্টে পুনর্নির্মাণ (পুরনো v8 `merge/backup/`-এ)
- `improve/round3/track-c/lse_writeback_300.py` — CCITT Width/Height spec-driven (এক লাইন; ব্যাকআপ `merge/backup/lse_writeback_300-pre-r5merge.py`)

**পুনর্নির্মিত স্টেজিং (পুরনো আউটপুট `merge/backup/`-এ):**
- `improve/round4/merge/db/lse_gravora.db` + `built/` (LSE-0008/0009, নতুন ফন্ট)
- `improve/round4/track-d/lse_gravora_copy.db` + merged PDF + label (LSE-0008 / LBL-0001, নতুন ফন্ট)
- `improve/round5/track-c/` — LSE-0012 / LBL-0005 (LSE-0011 supersede করা; verifier-এর stale SHA চেক আপডেট করা)
- `improve/round5/track-b/scripts/` — May LSE-0009 / LBL-0002 (নতুন ফন্ট; mechanism-test নোট অপরিবর্তিত)

**অপরিবর্তিত:** `REPORT.md`, `REPORT-MAY.md`, `ROUND2/3/4-REPORT.md`; শেয়ার্ড Round 3 DB (`lse_gravora.db`: LSE-0001–0007, ২০ entry); v7 (200-DPI) পাতা; `segment.py`, `inpaint.py`, `heading.py`, `build_page300.py` (কোনো বদল নেই — over-split ও sig_y fix Round 6-এ)।

**Suite আবার চালানোর উপায় (scan-paper/ থেকে):**
```bash
venv/bin/python3 fontfix_verify300.py        # 45/45
venv/bin/python3 verify_round2_300.py         # 18/18
venv/bin/python3 repro300.py                  # PASS
venv/bin/python3 manual_proof300.py           # 10/10
venv/bin/python3 improve/round2/matcher.py     # WIDTH 300 DPI (DNA #1 দুই পাতাতেই)
venv/bin/python3 improve/round4/track-b/matcher.py  # WIDTH 200 DPI (DNA #3 — রেকর্ড করা trade-off)
venv/bin/python3 improve/round4/merge/verify_writeback300.py   # 41/41
venv/bin/python3 improve/round4/track-d/verify_track_d1.py    # 47/47
venv/bin/python3 improve/round5/track-c/verify_track_c_r5.py  # 74/74
venv/bin/python3 improve/round5/track-b/scripts/verify_may_multipage.py  # 59/59
venv/bin/python3 improve/round4/track-d/sqlcipher_test.py      # 14/14
```

---

*Drive-এ কিছু আপলোড করা হয়নি (নির্দেশ অনুযায়ী)। মূল রিপোর্টগুলো বদলানো হয়নি।*
