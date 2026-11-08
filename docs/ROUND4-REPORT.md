# LSE Round 4 — চূড়ান্ত রিপোর্ট (MERGE)

**তারিখ:** 2026-11-06 · **স্থিতি:** সম্পূর্ণ — সব ট্র্যাক মার্জ + স্বাধীন যাচাই শেষ
**মূল নীতি (ব্যবহারকারীর স্থায়ী নিয়ম):** ডকুমেন্টের সম্পূর্ণ originality রক্ষা করতে হবে — original যে DPI-তে আছে, সেই DPI-তেই কাজ করতে হবে; কখনও downscale নয়, background re-encode নয়, resolution বদল নয়; সব ডকুমেন্ট টাইপ, সব DPI, সব স্ক্যানের জন্য।

## সারাংশ — এক নজরে

Round 4-এর ৪টি ট্র্যাকের কাজ একটাই মার্জ করা পাইপলাইনে (v4-300) আনা হয়েছে, এবং প্রতিটি দাবি আমি নিজে আবার চালিয়ে মেপেছি। **মূল ফল:**

| বিষয় | আগে (Round 3) | এখন (Round 4 মার্জ) |
|---|---|---|
| পাইপলাইন DPI | 200 DPI + q92/q95 re-encode (কোথাও native নয়) | **native 300 DPI end-to-end** — segmentation → live page → edited PDF |
| fontfix-verify | 35/35 (200 DPI) | **45/45** (300 DPI, clean-bg চেক সহ) |
| verify_round2 | 18/18 (200 DPI) | **18/18** (300 DPI) |
| repro (doubling) | PASS | **PASS** |
| manual_proof | 10/10 | **10/10** |
| PDF write-back | 40/40 (v2.1) | **41/41** (মার্জ, fs fix সহ) |
| Track D multipage | 47/47 (staging) | **47/47** (নতুন ফন্ট+বিল্ডারে আবার তৈরি করে) |
| Track D SQLCipher | 14/14 | **14/14** |
| Segmentation নমুনা (১৪ পাতা) | 513/518 (v4-200) | **518/518 সত্য শব্দ** |
| Title | 12/14 (v4-200: 5/12 নতুন পাতায় ভঙ্গুর) | **14/14** |
| H2 guard | 10/14 | **14/14** |
| Rotation (Raviraj) | 26/27 (p05 miss) | **27/27** |
| DNA WIDTH-জয় | Aug tie, May ৩য় | **200 DPI-তে জয় (0.482 / 0.609) — কিন্তু 300 DPI-তে নয় (নিচে দেখুন)** |

**সবচেয়ে বড় ধরা (মার্জের সময়):** Aug v8 পাতায় টাইপ করা লেখা আসল কালির উপর **doubling** হয়ে যাচ্ছিল — clean background আদৌ লাগছিল না। কারণ: Aug clean JPEG q95-এর base64 2,380,472 অক্ষর, আর Chromium-এর `setProperty` এত লম্বা CSS custom property নীরবে ফেলে দেয় (1.8M অক্ষর চলে, 2.38M চলে না)। সব text-চেক পাস করছিল, শুধু চোখে দেখলেই ধরা পড়ে। **ঠিক করা হয়েছে:** Aug clean q95 → q88 (1.41M অক্ষর), Lot "207/9" এখন পরিষ্কার, কোনো doubling নেই। এই বাগ ধরার জন্য fontfix-verify-তে ৪টি নতুন clean-bg চেক যোগ করা হয়েছে (এখন 45/45)। Track A-র v8 পাতাতেও একই বাগ ছিল — তাদের suite ধরতে পারেনি, কারণ কোনো চেকই clean background আসলে লেগেছে কি না দেখত না।

---

## ১. Track A — Native-300-DPI পাইপলাইন ✅ (মার্জ করা)

**কাজ:** পুরো পাইপলাইন native DPI-তে — segmentation, live page, write-back।
**মার্জ ফল (আমার নিজের রেন্ডারে মাপা):**

| ডকুমেন্ট | native DPI | seg শব্দ | নমুনা (rows 01–05) | live-page background | write-back |
|---|---|---|---|---|---|
| Aug p1 | 300 (JPEG) | 306 | 37/37 | original JPEG bytes, SHA ✓ | bg byte-identical, IoU 1.000 |
| Aug p2–p8 | 300 (JPEG) | 304–312 | 37–38/37 (৪টি speck FP) | — | — |
| May p1 | 300 (CCITT) | 311 | 37/37 | lossless PNG decode, 0 px differ | CCITT byte-identical, IoU 1.000 |
| May p2–p6 | 300 (CCITT) | 307–313 | 37–39/37 (৪টি speck FP) | — | — |

- **Originality audit:** ৬টি ডকুমেন্টই native 300 DPI-তে ঢোকে; live page-এ Aug background original JPEG bytes (SHA `7b171751…`), May background CCITT-র lossless PNG decode (0 px differ)। Write-back PDF-এর p1: May সত্যিই **0 px** (original-এর বাইরে), Aug **0 excess** (495,255 px = JPEG decoder baseline ঠিক)। Ink IoU **1.000/1.000** দুই পাতাতেই।
- **Clean layer সৎ সীমা:** clean layer-টি derived (inpainted), byte-identical নয় — q88-তে lossless PNG-র সঙ্গে max diff 21/255, mean 0.89 (q95-তে ছিল 26/0.70)। শুধু background-ই original bytes; clean-এর lossless PNG `cleans/`-এ archive হিসেবে রাখা আছে।
- **Segmentation native DPI-তে ভালো:** May 33/37 → **36–37/37** (নমুনা), Aug 37/37 ধরে রাখা।
- **May v8 পাতা উল্টো দেখানোর বাগ (Track A-র):** May-র working PNG rotated-upright decode, কিন্তু template CSS background 180° ঘোরায় — stored-orientation PNG (`pages/may-p1-orig-stored.png`, SHA `d0fb6f89…`, v6-র `may-p1-orig.png`-এর সঙ্গে **0 px differ**, শুধু PNG encoding আলাদা) ব্যবহার করতে হয়। চোখে দেখে যাচাই করেছি — May v8 পাতা সোজা।

## ২. Track B — DNA ফন্ট ✅ (মার্জ করা, কিন্তু WIDTH-জয়ে সৎ সীমা আছে)

**কাজ:** (১) digit advance fix, (২) sans clone set বাড়ানো, (৩) ttfautohint।

### (১) Digit advance — 200 DPI-তে জয়, 300 DPI-তে নয় ⚠️

- **প্রমোট করা ফন্ট:** `improve/round2/dna-prod/dna-clone-regular-600.ttf` (40 glyph) + `dna-clone-bold-600.ttf` (36 glyph) — Track B-র extended ফন্ট। পুরনো ফন্ট `merge/backup/dna-prod/`-এ ব্যাকআপ আছে। Digit advance যাচাই করেছি: v1b-র সঙ্গে **হুবহু এক** ('7' 532, '8' 551, '.' 221, '/' 532 — আগের 557/583/246 থেকে কম)।
- **Matcher v3 live-fit IoU (আমি নিজে চালিয়েছি):**

| শব্দ | 200 DPI (Track B-র matcher, প্রমোট ফন্টে আবার চালানো) | 300 DPI (মার্জ matcher) |
|---|---|---|
| Aug WIDTH "780.0"→"781.5" | **DNA 0.482 (১ম)** ✓ (Serif Bold 0.443) | Serif Bold **0.490 (১ম)**, DNA 0.449 (২য়) |
| May WIDTH "670.0"→"671.5" | **DNA 0.609 (১ম)** ✓ (Sans Bold 0.563) | Sans Bold **0.546 (১ম)**, DNA 0.498 (৩য়) |
| Aug Lot "206/7"→"207/9" | DNA 0.617 (১ম) ✓ | DNA 0.590 (১ম) ✓ |
| May Lot "304/5"→"305/7" | DNA 0.520 (১ম) ✓ | DNA 0.539 (১ম) ✓ |
| Title (৪টি) | DNA Bold ১ম ✓ | DNA Bold ১ম ✓ (0.588 / 0.597 / 0.511 / 0.512) |
| Page shortlist | DNA ১ম+২য় | DNA ১ম+২য় (Aug 0.593/0.519, May 0.518/0.512) |

- **সৎ কথা:** Track B-র দাবি "DNA WIDTH-এ দুই পাতাতেই জেতে" — আমি **200 DPI-তে হুবহু পুনরুৎপাদন করেছি** (Track B-র `matcher-final.txt`-এর সঙ্গে ৩ দশমিক পর্যন্ত মিলে)। কিন্তু **300 DPI-তে (মার্জ পাইপলাইন, আসল ডেলিভারেবল) DNA WIDTH-এ জেতে না** — Aug-এ Serif Bold, May-এ Sans Bold এগিয়ে। Advance fix 300 DPI-তে DNA-র WIDTH IoU-কে প্রায় বাড়ায়নি (Round 3 baseline Aug 0.446 → 0.449, May 0.490 → 0.498)। কারণ সম্ভবত: 300 DPI-তে fitWidth shrink অনুপাতে বেশি (May WIDTH fs_live/fs0 = 36.4/40.0 = 0.91, 200 DPI-তে 24.4/25.7 = 0.95) — shape মিল ভালো (IoU_vec 0.705) কিন্তু live-fit-এ পিছিয়ে। **তবে ব্যবহারকারীর চোখে ফল ভালো:** live পাতায় টাইপ করা WIDTH বাক্সের প্রস্থে হুবহু বসে (fontfix ratio Aug 1.00, May 0.99)। IoU_live shape-overlap মাপে, "বাক্সে ঠিক বসেছে কি না" মাপে না — দুই মেট্রিকের মতভেদ Round 5-এ খতিয়ে দেখতে হবে।
- **Single-glyph IoU অপরিবর্তিত** (0.712/0.613) — shape-এ কোনো আপস নেই।

### (২) Sans clone extension ✅
- Regular 'B' আসল নমুনা থেকে (BRIGHT/MATT, NUMBEROFJOINTS, PRINTIBILITY); bold digit/H/K/'/' regular median dilate করে। Fallback audit: BLISTER 6/7→**7/7**, bold "207/9" 0/5→**5/5**, CHECK 3/5→**5/5**, bold "780.0" 1/5→**5/5**; bold "207/9" width error 9.1%→3.0%। পুরনো glyph byte-identical।

### (৩) ttfautohint ❌ — ইনস্টল করা, কিন্তু প্রমোট করা হয়নি
- ttfautohint 1.8.4 কাজ করে, কিন্তু **matcher-কে খারাপ করে** (May WIDTH 0.609→0.505, DNA ১ম হারায়) এবং ফাইল +860%/+452% ফোলায়। fontfix-verify hint ছাড়াই 35/35 — hinting-এ কোনো লাভ নেই। **Unhinted + 0.97 margin রাখা হয়েছে।**

## ৩. Track C — Rotation + Segmentation hardening ✅ (মার্জ করা)

### (১) Rotation — 27/27 ✅
- Detector (`rotate_detect.py`, প্রমোট করা হয়েছে `scan-paper/`-এ; Tesseract 5.3.4 লাগে — এই VM-এ ইনস্টল করা হয়েছে): projection-profile axis → Tesseract OSD flip → flip3 override।
- **সব ২৭টি Raviraj পাতা 300 DPI-তে সঠিক** (p01–p02 → 90° CW, p03–p27 → 0°)। Track C-র একমাত্র miss **p05 এখন সঠিক** (চোখে দেখে যাচাই: dense numeric packing list, সোজা) — 300 DPI-তে signal পরিষ্কার (proj 202 বনাম 116, OSD conf 10.03)।
- **Raviraj end-to-end (p1, 300 DPI):** auto-rotate 90° CW → 508 শব্দ → From/To border ফিল্টার, PETRAPOLE নিজের বাক্স [1906,1355,2121,1383] ✓, BENAPOLE [1910,1501,2104,1529] ✓, Consignment No. [1894,1186,2028,1223] ✓, Consignment Date ৩ বাক্সে ("08."+"08."+"2026", এডিট করা যায়) ✓, R1 Corporate Office ব্লক চোখে দেখে যাচাই (প্রতিটি শব্দ আলাদা বাক্স, `:` নিজের বাক্স; `: 033-22851286` merge ঠিক)। p2: 494 শব্দ, p3: 460 শব্দ (v4-200: 498/412 — p3-তে বাড়তি শব্দ ছোট ছাপার finer split; মাত্র ৩/৪৮ unmatched বাক্স tiny speck)। p2/p3 শব্দ-ধরে-শব্দে হাতে যাচাই করা হয়নি (সীমা)।

### (২) Segmentation hardening (v4-300) — 518/518 ✅
- **১৪ পাতার নমুনা (rows 01–05, হাতে গোনা ৩৭টি সত্য শব্দ/পাতা): 518/518** — প্রতিটি সত্য শব্দ আলাদা বাক্সে। বাড়তি মাত্র **৪টি speck FP** (Aug p2/p6/p8, May p5 — ৪–১০ px ধুলো)।
- **Title 14/14** (Aug p1–p8 ও May p1–p6 সব ৩ বাক্স)। May p1/p2/p6-এ title-র উপরে ছোট speck/sliver FP আছে (২+১+১) — title শব্দ ঠিক, speck-গুলো cosmetic।
- **Sig-row leak ঠিক:** Aug p5-এ sig_y-র নিচে 0 বাক্স (v3-তে ১৩টি)।
- **Decimal split ঠিক:** Aug p8-এ 700.0 / 0.0254 / 68.83 / 7.59 এক বাক্সে।
- **Rule/border filter:** Raviraj From/To বর্ডার আর বাক্স পায় না (w>400, h 50–100: none)।
- **FOIL TEMPER:** Aug/May p1–p3 সব ৬ পাতায় split (v4-200 May-তে ৫/৬ পাতায় merge হত)।
- **জানা over-split (খোলা আছে):** Aug p8 THICKNESS, May p3 THICKNESS + GRAMMAGE — ২.০× median-এ letter gap-ও qualify করে। `<3 subs merge` নিয়ম চেষ্টা করেছিলাম — **আরও খারাপ হয়েছে** (−৭ শব্দ/পাতা, আসল dash/dot/ছোট শব্দ merge হয়ে যায়), তাই **ফিরিয়ে নিয়েছি**। শব্দগুলো পুরো cover আছে, শুধু দুই টুকরোয় এডিট করতে হয়। Round 5-এ gap-size ছাড়া অন্য discriminator (width/lexicon চেক) লাগবে।

### (৩) H2 guard — 14/14 ✅
- `heading_lines_guarded` (structural: title-র নিচে + প্রস্থ ≥0.82×page + ≥6 বাক্স + আগের লাইন ছোট + rule band-এর নিচে) **১৪/১৪ পাতায় সঠিক header লাইন** ধরে (cy ~1136–1164, ৭–৯ বাক্স, প্রস্থ ~2102)। fontfix-verify 45/45 অটুট। সীমা: প্রস্থ margin মাত্র ৩৮ px; নিয়মটি PG-template-এর আকারের, universal নয়। Aug p4 H1-র greyest-fallback ছাড়াই H1-তে ধরা পড়ে (H1b fix-এর জন্য)।

## ৪. Track D — DB / GRAVORA গভীরতা ✅ (আবার তৈরি করে যাচাই)

- **Multi-page delivery:** LSE-0008 (Aug p1+p2, একটাই ৫-পাতার PDF) — নতুন ফন্ট+বিল্ডারে **আবার তৈরি করে** যাচাই: verify_track_d1.py **47/47**। প্রথমে ৪টি ink-IoU চেক ফেল করেছিল (0.499–0.620) — কারণ Track D-র পুরনো staging PDF v7 ফন্টে বানানো, আর reference নতুন extended ফন্টে রেন্ডার হচ্ছিল। Staging আউটপুট আবার তৈরি করায় সব IoU **1.000**। পুরনো আউটপুট `merge/backup/track-d/`-এ রাখা আছে।
- **label_ref:** LSE-0008 → LBL-0001, লেবেলে এডিট করা মান (Batch 207/9, WIDTH 781.5 mm) ✓।
- **Bengali certificate:** Chromium/HarfBuzz পথে সঠিক (conjuncts ক্ষতি, জ্ঞান, বিস্তার… ঠিক; Bengali digit ২০৭/৯, ৭৮১.৫) — তবে এখনও merged PDF-র p5-এ ঢোকানো হয়নি (standalone প্রমাণ)।
- **SQLCipher:** sqlcipher_test.py **14/14** — key ছাড়া / ভুল key-তে "file is not a database"; chain + hash সব মেলে। Production key management (Secure Vault/KDF) এখনও ডিজাইন হয়নি — demo key মাত্র।
- **v2 interface:** `LSEDeliveryState v2` (pages[] + label_ref) — শেয়ার্ড Round 3 DB-তে প্রমোট করা হয়নি (সেটি অটুট: LSE-0001–0007, ২০ entry)। Track D-র কোড `improve/round4/track-d/`-এ reference implementation হিসেবে আছে।

## ৫. মার্জের সময় ধরা বাগ (সব ঠিক করা হয়েছে)

| # | বাগ | কীভাবে ধরা পড়ল | ঠিক |
|---|---|---|---|
| 1 | Aug p1 title ৩→৫ বাক্সে ভেঙে গেল | নমুনা চেক | Hollow-border filter-এ **edge fraction ≥0.40** (fill নয় — fill DPI-ভেদে বদলায়; title-র halftone mesh 0.044, আসল বর্ডার 0.688/0.780) |
| 2 | Raviraj বর্ডার 300 DPI-তে ফিল্টার হলো না | চোখে দেখা | Edge band 3→**5 px** (DPI-স্কেল; frame line ৫–৬ px মোটা) |
| 3 | Aug p7 title "ANALYTICAL TEST" merge | Title চেক | TOP-2 mult 2.2→**2.0** (normal subs); 1.5× over-split করেছিল (+১৭–২১ শব্দ/পাতা) |
| 4 | May p4 title ২.০×-এ merge | Title চেক | **Eroded subs 1.5×** (erosion সব gap ফুলিয়ে দেয় — median ৬ বনাম ৪) |
| 5 | THICKNESS/GRAMMAGE over-split | নমুনা চেক | `<3 subs merge` চেষ্টা করে **ফিরিয়ে নেওয়া** (আরও খারাপ); খোলা item হিসেবে রাখা |
| 6 | **Aug v8-তে doubling (গুরুতর)** | **চোখে দেখা** (Lot clip) | Clean q95→**q88**; fontfix-এ ৪টি clean-bg regression চেক যোগ |
| 7 | Lot ink IoU 0.519 (write-back) | Track A-র ধরা বাগ | `lse_writeback_300.py`-তে **fs full-precision** (এক লাইন); এখন IoU 1.000 |
| 8 | Track D IoU 0.5 (ফন্ট বদলের পর) | verify re-run | Staging আউটপুট নতুন ফন্ট+বিল্ডারে আবার তৈরি |

**মার্জ-শিক্ষা:** fill threshold DPI-ভেদে বদলায় (halftone dither) — structural metric (edge fraction, DPI-স্কেল band) ব্যবহার করো। TOP-2-র multiplier পুরনো every-gap নিয়মেরটা (2.2×) সরাসরি চলে না। ১ px রেন্ডার পার্থক্যে speck FP আসে/যায় — কোন রেন্ডারে সংখ্যাটা মাপা হয়েছে, সেটা লিখতে হবে। **Text-চেক পাস করলেই যথেষ্ট নয় — clean background আসলে লেগেছে কি না, চোখে দেখে যাচাই করতে হবে।**

## ৬. চূড়ান্ত যাচাই তালিকা (সব আমি নিজে চালিয়েছি)

| চেক | ফল |
|---|---|
| fontfix_verify300.py (৩০০ DPI, v8 পাতা) | **45/45** |
| verify_round2_300.py (identity probe + doubling + D1 + pixel-diff) | **18/18** |
| repro300.py (doubling) | **PASS** |
| manual_proof300.py (signature cover, residue 0) | **10/10** |
| verify_writeback300.py (মার্জ staging DB, ৪১ চেক) | **41/41, FAILURES: none** |
| verify_track_d1.py (multipage + label_ref) | **47/47** |
| sqlcipher_test.py (encrypted DB) | **14/14** |
| Matcher 300 DPI (প্রমোট ফন্ট) | DNA: Lot ২/২, Title ৪/৪; **WIDTH ০/২** (নিচে) |
| Matcher 200 DPI (প্রমোট ফন্ট, Track B পুনরুৎপাদন) | DNA: WIDTH ২/২ (0.482 / 0.609), Lot ২/২, Title ৪/৪ |
| Segmentation নমুনা ১৪ পাতা | **518/518** সত্য শব্দ (+৪ speck FP) |
| Title ১৪ পাতা | **14/14** |
| H2 guard ১৪ পাতা | **14/14** |
| Rotation (Raviraj ২৭ পাতা) | **27/27** |
| Raviraj p1 (border/PETRAPOLE/BENAPOLE/R1) | ✅ |
| চোখে দেখা (v8 Aug/May পাতা, Lot/WIDTH clip) | ✅ (doubling ঠিক হওয়ার পর) |

**Identity probe (row label + box — position নয়):** Aug Lot "207/9" [533,930,631,966], WIDTH "781.5" [2088,1282,2178,1310]; May Lot "305/7" [521,913,619,950], WIDTH "671.5" [2078,1290,2169,1318]; "Hard" দুই পাতাতেই অক্ষত।

## ৭. সৎ সীমা — যা এখনও সম্পূর্ণ নয়

1. **DNA WIDTH-জয় 300 DPI-তে হয়নি** (§২ দেখুন)। Advance fix আসল, কিন্তু live-fit ranking 300 DPI-তে Serif/Sans Bold-কে এগিয়ে রাখে। Round 5-এ খতিয়ে দেখতে হবে (fitWidth/cap-height আচরণ বড় size-এ)।
2. **৩টি over-split শব্দ** (THICKNESS ×২, GRAMMAGE ×১) — gap-size দিয়ে আলাদা করা যায় না; নতুন discriminator লাগবে।
3. **৪টি speck FP** নমুনায় + May title-র উপরে speck/sliver (cosmetic)।
4. **Raviraj p2/p3** শব্দ-ধরে-শব্দে হাতে যাচাই হয়নি (শুধু p1-র key region)।
5. **Print calibration** — VM-এ প্রিন্টার নেই; কারখানার প্রিন্টারে করতে হবে (পদ্ধতি `improve/round2/print-calibration.md`-এ)।
6. **US patent US20150332491A1** — বিক্রির আগে আইনজীবীর যাচাই লাগবে (আমার কাজ নয়)।
7. **DBNet swap** এখনও deferred (classical primary)।
8. **Bengali certificate** merged PDF-র p5-এ ঢোকানো হয়নি; **label demo-stage** (শুধু p1-র WIDTH); **May multi-page / ৩+ পাতা** যাচাই হয়নি; **SQLCipher key management** ডিজাইন হয়নি।
9. **v7 (200-DPI) পাতা** অটুট আছে (frozen artifact); v8 (300-DPI) পাতাই এখন canonical।

## ৮. যা বদলেছে (শেয়ার্ড ট্রি) — প্রমোট তালিকা

**বদলানো ফাইল (ব্যাকআপ `improve/round4/merge/backup/`-এ):**
- `segment.py` (v4-300), `inpaint.py` (300 DPI), `heading.py` (300 DPI + guarded H2)
- `improve/round2/matcher.py`, `conf.py`, `manual_clean.py` (300 DPI; conf এখন merged v4-300 seg পড়ে — Track C-র conf_v4 fix)
- `improve/round2/dna-prod/dna-clone-regular-600.ttf` (40 glyph), `dna-clone-bold-600.ttf` (36 glyph) — Track B extended (পুরনো `merge/backup/dna-prod/`-এ)
- `improve/round3/track-c/lse_writeback_300.py` — fs full-precision (এক লাইন)

**নতুন ফাইল:**
- `rotate_detect.py`, `rotate_proj.py`, `rotate_flip3.py` (rotation, Tesseract লাগে)
- `build_page300.py`, `fontfix_verify300.py`, `verify_round2_300.py`, `repro300.py`, `manual_proof300.py`
- `pages/aug-p1-300.png`, `pages/may-p1-300.png`, `pages/may-p1-orig-stored.png`, `seg-aug-p1-300.json`, `seg-may-p1-300.json`, `cleans/` (clean + manual clean, 300 DPI)
- `live-scan-page-aug-300.html` (3,614,893 B), `live-scan-page-may-300.html` (2,049,588 B) — **v8 পাতা**
- `heading-aug-300.json`, `heading-may-300.json`
- `improve/round4/clips/` (যাচাই স্ক্রিনশট), `improve/round4/merge/` (মার্জ স্ক্রিপ্ট, seg, রেন্ডার, staging DB/PDF)

**অপরিবর্তিত:** `REPORT.md`, `REPORT-MAY.md`, `ROUND2-REPORT.md`, `ROUND3-REPORT.md`; Round 3 শেয়ার্ড DB (`lse_gravora.db`: LSE-0001–0007, ২০ entry); v7 পাতা; Track D-র মূল কোড (শুধু staging আউটপুট আবার তৈরি)।

**Suite আবার চালানোর উপায় (scan-paper/ থেকে):**
```bash
venv/bin/python3 fontfix_verify300.py        # 45/45
venv/bin/python3 verify_round2_300.py         # 18/18
venv/bin/python3 repro300.py                  # PASS
venv/bin/python3 manual_proof300.py           # 10/10
venv/bin/python3 improve/round4/merge/verify_writeback300.py   # 41/41
venv/bin/python3 improve/round4/track-d/verify_track_d1.py    # 47/47
venv/bin/python3 improve/round4/track-d/sqlcipher_test.py      # 14/14
venv/bin/python3 improve/round2/matcher.py     # page_rank + WIDTH (300 DPI)
venv/bin/python3 improve/round4/track-b/matcher.py  # WIDTH (200 DPI, Track B পুনরুৎপাদন)
```

---

*Drive-এ কিছু আপলোড করা হয়নি (নির্দেশ অনুযায়ী)। মূল রিপোর্টগুলো বদলানো হয়নি।*
