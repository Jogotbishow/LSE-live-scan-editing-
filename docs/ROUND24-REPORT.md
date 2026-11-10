# LSE Round 24 — রিপোর্ট

**তারিখ:** 2026-11-09 · **ভাষা:** বাংলা · **মার্জ এজেন্ট:** Round 24 coordinator
**Baseline:** Round 23 merged segmenter + gate (`round23/merge-r23/`, gate 23/2) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round24/merge-r24/` (segment_merged.py + gate_merged.py + rhythm_dp.py + logo_detect.py + gate_misses.py + segs/)
**ডিরেক্টরি:** `improve/round24/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r24/`-তে
**নির্দেশ:** ব্যবহারকারীর LSE 100% নিয়ম (2026-11-08 22:42) — Muse নিজে 100% সন্তুষ্ট না হওয়া পর্যন্ত LSE-র কাজ থামবে না; কোনো অনুমতি লাগবে না। এই রাউন্ড সেই নির্দেশেই চলেছে।

> **সৎ সারাংশ:** Gate 23/2 → **23/2 — অপরিবর্তিত**। ৬টি ট্র্যাকের একটিও PROMOTE হয়নি — p20-র fused লাইন, p21-র ৭-শব্দ stretch, আর p21 heading — তিনটিই এখন **প্রমাণিত geometry-only known limit** (তিনটি স্বাধীন প্রমাণ: diagnosis + দুটি fix-প্রচেষ্টা + greyscale পরীক্ষা)। এটা পিছিয়ে যাওয়া নয়, আবার এগোনোও নয় — এই রাউন্ডের ফসল **প্রমাণ** (সীমাগুলি আসল, চেষ্টার অভাব নয়) আর Round 25-র জন্য সুনির্দিষ্ট নতুন পরীক্ষা (Omron M, skeleton-graph, reduced underline)। কোডে কোনো বদল নেই বলে merge-r24 R23-র সঙ্গে byte-identical — সেটাই সৎ merge। 25/0 দেখাতে gate-কে warn-only করা বা ভুল cut-কে promote করা হতো **অসততা** — দুটো fix ট্র্যাকই gate-এ 24/1 পেয়েছিল ভুল cut দিয়ে (§৬-এ blind spot), আর দুটোতেই word-identity যাচাই (0/4) সেটা ধরে ফেলেছে।

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R23 baseline | **Round 24 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 23 ALLOW / 2 REFUSE | **23 ALLOW / 2 REFUSE (=)** |
| ফ্ল্যাগ (T1 / T2 / T3) | 2 (0 / 0 / 2) | **2 (0 / 0 / 2) (=)** |
| মোট শব্দ (২৫ পাতা) | 9373 | **9373 (=)** |
| মোট শব্দ (৩৩ পাতা) | 12366 | **12366 (=)** |
| REFUSE পাতা | p20 + p21 | **p20 + p21 (=)** |
| Canonical p2 N5 / Description ভুল / redbox | 41/81, ভুল ৩০, 7/66 | **41/81 (=), ভুল ৩০ (=, একই list), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 248 / 285 (186) | **248 (=) / 285 (=) (186, =)** |
| Canonical p2 / p3 gate | p2 ALLOW, p3 ALLOW | **p2 ALLOW, p3 ALLOW (=)** |
| LINES (canonical r15m) | 327/327 | **327/327 (=)** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/313/306 | **aug 306/308/305, may 308/313/306 — হুবহু একই** |
| p21 GT (৪২ certain boundary) | 36/42 @ ±5px meet-rule | **36/42 (=, seam ট্র্যাক স্বাধীনভাবে পুনরুৎপাদন করেছে)** |
| Guard (live page, FULL) | 5/5 | **5/5 PASS (segs byte-identical বলে অপরিবর্তিত)** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |
| Full suite (repo test clone) | 38/38 | **38/38 PASS (434.02s, 0 fail)** |
| Demo (synthetic) | 82 শব্দ | **82 শব্দ (=, নিজে চালিয়ে যাচাই)** |
| Aug p1 শব্দ-সংখ্যা | PNG 306 / fitz 308 | **PNG 306 / fitz 308 — দুই render-পথেই সঠিক** |

**ফ্লিপ:** কোনোটিই নয় — ২৩টি ALLOW পাতার একটিও regress হয়নি, আর p20/p21-র একটিও ALLOW হয়নি। **Promotion bar-এর রায়: কোনো code promote হয়নি — সৎভাবে।** T3 recall 35/35 (100%) অপরিবর্তিত, coverage 95/97 অপরিবর্তিত। এই রাউন্ডে যা বদলেছে তা হলো **জ্ঞান**: p20-র লাইন আর p21-র stretch/heading geometry-only toolset-এর প্রমাণিত সীমা — আর সেই সীমার ঠিক পরের পরীক্ষাগুলি (§১০)।

---

## ১. ট্র্যাক verdicts — ৬টি ট্র্যাক, সব DONE, একটিও PROMOTE নয়

| ট্র্যাক | verdict | মূল ফল |
|---|---|---|
| **track-p20diag** | **NO separating signal (প্রমাণসহ)** | ৩টি সত্য boundary সব live signal-এ **প্রতিটি** intra-word gap-এর চেয়ে খারাপ — পার্থক্য উল্টো দিকে: bridge ratio 0.99/1.11/1.04 বনাম gap 1.22–1.39 (সীমানা সব gap-এর চেয়ে শক্ত bridge); seam cost সত্য সীমানায় worst gap-এর **৩.৫–৫.৩×**; count-driven cut ০ ভালো valley (পুনরুৎপাদন); PNG vs fitz **ZERO drift** (p20-তে)। সুপারিশ: bridge/seam দুটোই ছাড়ো; separator-glyph বা greyscale-aware re-segmentation ছাড়া line known limit। |
| **track-p20bridge** | **DO NOT PROMOTE** | Greyscale-bridge (diagonal white-wedge, LIGHT=200, DIAG_INK=215, slope −0.5, score ≥0.8): p20-তে **0/4 সত্য শব্দ, ৫টি ভুল cut** (rel 22/46/94/182/311 — সত্য cut ~117/258/343-এর ৩০px-এর মধ্যেও নয়)। Gate 24/1 (p20 ALLOW) — **FALSE** (§৬)। ৩৩ পাতায় শুধু p20 বদলায় (521→526), বাকি ৩২ পাতা byte-identical; fitz ১৪ পাতা box-identical, Aug p1 308। EP0780782 lead মাপা প্রমাণে বন্ধ। |
| **track-p20seam** | **DO NOT PROMOTE** | Lee & Oh min-cost seam (DP, greyscale cost, ±5px corridor, Path-C guard): p20-র লাইন **৮ টুকরো, ৪ শব্দ নয়**; ৩টি সত্য সীমানার ১টি পেয়েছে (817), বাকি ৬টি seam ২৯–৮৮px শব্দের ভেতরে; **0/4 সত্য শব্দ** (best IoU 0.627 — \"TER/SHIPPE\", শব্দ নয়)। Gate 24/1 — **FALSE** (§৬)। ৩৩ পাতায় শুধু p20 বদলায় (521→528); fitz identical, Aug p1 308; canonical identical; p21 GT 36/42 পুনরুৎপাদন। |
| **track-p21stretch** | **DO NOT PROMOTE — ACCEPTED KNOWN LIMIT** | EP0780782 greyscale pixel-bridge classification (per-scan-line margin: WEAK/MODERATE/STRONG) সত্য/ভুল আলাদা করে না: weak_frac TRUE 16/17 = 1.00, WRONG 17/19 = 1.00; সেরা threshold-এ ভুল **17/36 = chance**। `of\|expiry` স্পষ্টভাবে মাপা (Otsu gap 0, dark run 4, weakest touch — কিন্তু ভুল cut TD/70- আর av\|i আরও শক্ত)। **সংশোধন (§৯):** R23-র \"৯ সঠিক / ১৫ ভুল\" আসলে **৮ সঠিক / ১৬ ভুল** (১৭ সত্য / ১৯ ভুল cut)। |
| **track-heading** | **DO NOT PROMOTE — KNOWN LIMIT (তৃতীয় পদ্ধতি-পরিবারেও)** | Greyscale profile: rule-band grey বনাম letter-ink grey histogram overlap **0.751**; সেরা threshold-এ balanced accuracy **0.625** @ grey 80 (chance 0.50; দরকার ~0.99)। Removal simulation **0/8** — আর নির্ণায়ক নতুন তথ্য: **নিখুঁত rule removal-ও 0/8** — bottleneck removal নয়, **grouping** (rule গেলে অক্ষর টুকরো হয়, জোড়া লাগানোর একমাত্র signal gap width — যেটা উল্টো)। 2D white-column আর vertical run-length-ও fail। |
| **track-online** | **গবেষণা (কোড নয়)** | RESEARCH24.md (২১২ লাইন, ২৬টি নতুন source, R21–R23-এর কোনোটি পুনরাবৃত্তি নয়)। Top 3 — (১) Omron US 9,710,945 / EP 2,816,504 greyscale min-projection P(x) + fitted line M; (২) EP0780782 module 14 adjacent-scan-line vote (10%-নিয়ম) + lowest-dip T + deconvolution সূত্র `Yp = yp + a·yp-1`, a = −0.06; (৩) US 10,586,125 reduced underline (heading-র নতুন lead)। আরও: skeleton-graph US 5,787,196, tree-indexed demarcation (Tang 2017), fuzzy vote (Farulla 2017)। **সৎ verdict: 2024–2026-এ geometry-only word segmentation-এ কোনো breakthrough নেই** — R22/R23-র negative এখনও বহাল; newest geometry-only কাজ ২০২০-এর। |

---

## ২. merge — কীভাবে R23 baseline অপরিবর্তিতভাবে এগিয়ে নেওয়া হলো

**নেওয়া হয়েছে:** কিছুই না — ৬টি ট্র্যাকের একটিও PROMOTE হয়নি, তাই merge-এ কোনো code hunk নেই।
**নেওয়া হয়নি:** p20bridge, p20seam, p21stretch v2 splitter, heading variant — সব DO NOT PROMOTE, ফাইল শুধু rejected experiment হিসেবে ট্র্যাক-ডিরেক্টরিতে আছে।

মার্জ-প্রক্রিয়া (পুনরুৎপাদনযোগ্য — স্ক্রিপ্ট `improve/round24/`-তে রাখা আছে):
- `merge_segment_r24.py` — R23 baseline-এর ৫টি ফাইল (segment_merged.py, gate_merged.py, rhythm_dp.py, logo_detect.py, gate_misses.py) SHA-256 দিয়ে যাচাই: **সব byte-identical** (segment `86541e29af96`, gate `d63779a41a87`, rhythm `7f8164c1fd2c`, logo `e770a25e6290`, gate_misses `77ad274294a9`)।
- `run_segs_r24.py` — ৩৩ পাতা re-segment: **৩৩/৩৩ box byte-identical** (R23 segs-এর সঙ্গে diff খালি); শব্দ 9373/12366 হুবহু।
- `run_gate_r24.py` — gate re-run: **ALLOW 23 / REFUSE 2, T1 0, T2 0**; ২৫ পাতার প্রতিটি SAME (R23 baseline-এর সঙ্গে); canonical p2/p3 ALLOW, PG ৬ পাতা ALLOW।
- `score_canon.py` (R21-র scorer, tag r24) — p2 N5/Desc/redbox SAME; p3 strict **248/384**, improved **285/384**, FP 186 — সংখ্যা হুবহু, শুধু file-path স্ট্রিং-এ r23→r24 বদল।
- **Repo test clone-এ port:** কোড অপরিবর্তিত বলে `~/workspace/lse-r23-test/`-এর পুরো কপি `~/workspace/lse-r24-test/` হিসেবে নেওয়া হয়েছে (`.git` ছাড়া); lse/segment.py-তে `_gap_mark` ৯টি, gate-এ Path C/check_dp_integrity ১০টি, EXP2/`_reclaim_core` ৭টি hit যাচাই করা হয়েছে; 0.92-র ৩টি hit শুধু comment-এ (R23-র মতোই)। Demo-তে port করা segmenter **৮২ শব্দ** দেয় (= R23)।

**Merge যাচাই (coordinator-এর নিজের run):** ৩৩ পাতা re-segment — শব্দ হুবহু; gate 23/2; canonical হুবহু; p21 GT 36/42 (seam ট্র্যাক স্বাধীনভাবে পুনরুৎপাদন: L1648 7/9, L1926 11/15, L2379 18/18); fitz Aug p1 **৩০৮** (email ২ শব্দ `[970,417,1080,450]` + `[1122,418,1272,450]`); ১৪টি PG পাতা fitz-এ segment করা হয়েছে; suite **38/38 PASS (434.02s)**।

---

## ৩. p20-র diagnosis — কেন fused লাইন geometry-তে ভাঙা যায় না

p20-র লাইন ২: box `[557,661,986,678]` — **"BENEFICIARY/MANUFACTURER/EXPORTER/SHIPPER"** (৪ শব্দ, slash-জোড়া, ৩টি CC ১১৭–১৫৮px)। Diagnosis ট্র্যাক ৩টি সত্য সীমানা (slash centre rel 125/255/340) মেপেছে একই লাইনের **১৮টি intra-word gap**-এর সঙ্গে — binary আর greyscale, দুটোতেই:

| Signal | সত্য সীমানা (৩টি) | ১৮টি intra gap | রায় |
|---|---|---|---|
| Column min grey, core band | 164 / 183 / 172 | 201–229 | সীমানা সব gap-এর চেয়ে **১৮–৩৭ level গাঢ়** |
| W_core (white rows, core band) | 0.00 / 0.00 / 0.00 | 0.33–1.00 | ৩ সীমানাতেই শূন্য সাদা row |
| Valley filt | 5.5 / 2.6 / 4.9 | 5.1–14.8 | B2 সব ৫৪টি valley-র নিচে |
| EP0780782 bridge ratio (min grey / 165) | 0.99 / 1.11 / 1.04 | 1.22–1.39 | সীমানা সব gap-এর চেয়ে **শক্ত bridge** (B1 < 1.0: slash stroke-এর চেয়েও গাঢ়) |
| Otsu ink px / column | 12 / 15 / 12 of 17 | 0–11 | সীমানা সব gap-এর চেয়ে বেশি কালিযুক্ত |
| Straight grey seam cost | 0.106 / 0.070 / 0.091 | 0.000–0.020 | সীমানা worst gap-এর **৩.৫–৫.৩×** |
| Solid bridge rows (<200 grey) | 9 / 5 / 9 of 9 | 0 of 9 | bridge পুরো core band জুড়ে |

**মূল কারণ — হালকা ছাপা + blur:** ink median grey 192 বনাম paper 232; Otsu 217 blur halo-কে ধরে সব এক করে দেয়। পুরো ৪২৯-কলাম box-এ মাত্র ২টি zero-ink কলাম আছে (১px @158, ২px @310–311) — দুটোই শব্দের মাঝখানে। মাত্র ৪৩টি dark (<141) pixel পুরো box-এ। **Slash-গুলো geometry:** slash ১-এ পরিমাপযোগ্য diagonal আছে (Hough slope −0.88); slash ২-এ কোনো clean diagonal নেই — R-এর leg যেখানে cross করেছে সেখানে smudge; slash ৩-এর একটি Hough diagonal (slope −1.00) হয়তো letter leg। তিনটি slash-ই দুই পাশের অক্ষরের সঙ্গে 8-connected — **সীমানাটি একটি stroke, space নয়; কাটার মতো কোনো gap নেই**।

**Count-driven cut (নির্ভুল পুনরুৎপাদন):** exp_n 9.13 → ৮টি cut চাই; top-8 valley width [1,2,0,0,0,0,0,0] → **০টি ভালো valley**। Rank ১–২ মাঝ-শব্দের Otsu gap; সত্য centre rank 39/54 (B1), 48/54 (B3); B2-র centre valley-ই নয়। Valley cutter প্রথম সত্য-ঘেঁষা gap-এর আগে ৭টি intra-word gap কাটবে।

**PNG vs fitz — p20-তে ZERO drift:** দুই render byte-identical (deskew নয়, 0.09°), Otsu একই (217), CC একই, raw fitz render-এ R23 segmenter-এ ৫২১ শব্দ, PNG seg-এর সঙ্গে box set identical। R23-র render-drift শিক্ষা এই পাতায় প্রযোজ্য নয় — কিন্তু যাচাই করা হয়েছে, ধরে নেওয়া হয়নি।

**সুপারিশ (diagnosis ট্র্যাকের):** greyscale bridge ছাড়ো (slash EP0780782-র সংজ্ঞায়ই শক্ত bridge); min-cost seam ছাড়ো (সৎ cost worst gap-এর ৩.৫–৫.৩×); **line-টি proven geometry-only known limit** ঘোষণা করো — যদি না game বদলানো কিছু আসে (separator-glyph ধারণা — `/`-কে নিজে শনাক্ত করে সরানো — বা greyscale-aware re-segmentation; দুটোই unproven, আর দুটোকেই ১৮টি intra gap-এ no-false-cut যাচাই পাস করতে হবে)।

---

## ৪. p21-র stretch — সৎ সিদ্ধান্ত: ACCEPTED KNOWN LIMIT

p21 `[827,1970,1317,2005]` — **"three months before the date of expiry"** (৭ শব্দ, ১ box, line 31, maxgap 6px)। এই রাউন্ডে শেষ untested signal-টি মাপা হয়েছে — EP0780782-র আসল per-scan-line classification (R23 শুধু সব row একসঙ্গে করে একটি ratio মেপেছিল; এই ট্র্যাক প্রতিটি core-band row-এ `margin = lightest-stroke-ink − darkest-bridge-ink` মেপেছে: WEAK >0, MODERATE −20–0, STRONG <−20):

- **weak_frac (EP0780782): TRUE ১৬/১৭ = 1.00, WRONG ১৭/১৯ = 1.00** — সেরা single-threshold-এ ভুল **17/36 = chance**। অন্য সব greyscale quantity-ও overlap করে (darkest 105–230 বনাম 20–238; escape 231–255 বনাম 225–255; margins, w140/w180/w220 — সেরা ভুল ৮–১৭/৩৬, সব post-hoc fitted threshold, overlap করা range-এ)। Halo-র grey word gap-এ আর letter gap-এ একই। Edge control প্রমাণ করে meter কাজ করে (solid ink edge weak = 0.00)। Deconvolution বাস্তবায়ন করা হয়নি — তার precondition (moderate-vs-strong split) অনুপস্থিত: touching নয় এমন সবকিছু দুই পাশেই WEAK।
- **`of|expiry` — স্পষ্টভাবে মাপা:** Otsu gap 0 (full band; core band-এ 4px), dark run 4 (full) / 8 (core), core run 4 / 7, darkest grey 105; per-row margin: ৯টি WEAK / ২টি MODERATE / ৭টি STRONG row (worst row 19: margin −76)। আসল touching bridge — **কিন্তু** দুটি ভুল touching cut একই রকম বা আরও শক্ত দেখায় (TD/70- min −103, av|i min −112), আর `of|expiry` তিনটির মধ্যে **সবচেয়ে হালকা** touch। আলাদা করা যায় না।

**সিদ্ধান্ত (সৎ):** p21-র stretch **accepted known limit**। যা দরকার হবে তা হলো recognition ছাড়া letter identity জানা একটি signal — "TRANS"+"PORT" এক শব্দ, "MAA"+"ANNAPURNA" দুই শব্দ, আর এই পার্থক্য letter sequence-এ আছে, আজ পর্যন্ত মাপা কোনো CC/gap/grey profile-এ নেই (R22/R23/R24-এ ১১টির বেশি quantity, সব overlap)। সেটা recognition — ব্যবহারকারীর নিষেধ। Gate-কে দুর্বল করে লুকানো যাবে না — p21 REFUSE-ই থাকবে, যতক্ষণ না এমন signal আসে।

**সংশোধন (§৯):** R23-র eye-verification-ও ঠিক করা হয়েছে — নিচে দেখুন।

---

## ৫. p21 heading — তৃতীয় পদ্ধতি-পরিবারেও unfixable (grouping-ই bottleneck)

p21 heading blob `[555,1082,1548,1119]` (৯৯৩×৩৭, fill 0.65), underlined। এই রাউন্ডে তৃতীয় পরিবার — **greyscale profile** (rule-র কালি বনাম অক্ষরের কালি grey level-এ আলাদা কি না):

- **Identification — greyscale FAIL:** rule-band grey (pure column, n=584 px): median 96, p5 79, p95 128; letter-ink grey (n=9935 px): median 90, p5 59, p95 115। **Histogram overlap 0.751**; darkest-50% core-ও overlap 0.501 (rule 88 বনাম letter 76)। সেরা single-threshold-এ balanced accuracy **0.625 @ grey 80** (chance 0.50; usable removal-এ দরকার ~0.99)। Symmetric darkest-quartile core overlap 0.159 — আসল physical পার্থক্য আছে (rule core letter core-এর চেয়ে ~১৪–২৫ level হালকা) কিন্তু separator হিসেবে অকেজো। Fused column-এ letter→rule সীমানায় কোনো grey step নেই (যেমন x=900: y1110 88 → y1111 68 → y1112 65, smooth)।
- **Removal simulation — 0/8** (THR=79-এ ৪৬ CC, THR=85-এ ৩৯ CC; প্রতিটি শব্দ ২–১২ টুকরো)।
- **নির্ণায়ক নতুন তথ্য — নিখুঁত removal-ও 0/8:** পুরো band সব কলামে মুছে দিলেও ৫৬ CC, প্রতিটি শব্দ ২–১২ টুকরো। **Bottleneck removal নয়, grouping** — rule গেলে অক্ষর CC-তে ভেঙে যায়, আর জোড়া লাগানোর একমাত্র signal gap width — যেটা উল্টো (letter-gap centre x=675-এর grey 245–254, word-gap centre x=701-এর ~189–210-এর চেয়ে পরিষ্কার)।
- **2D white-column — FAIL:** W_core সব ১১টি gap-এ 1.00; W overlap (word 0.86–0.92 বনাম letter 0.86–0.89)। Plateau height rule-এ আটকে; শুধু plateau width আলাদা — সেটা gap width-ই আরেক রূপে।
- **Vertical run-length — FAIL:** rule run ৩–৪px = letter horizontal stroke ৩–৫px (band-এর ওপরে ৭৪টি length-4 run); ৬০৯টি fused run letter+rule জুড়ে continuous।

**সৎ নোট:** ট্র্যাক নিজের দুটি মাপার ভুল ধরার আগেই ঠিক করেছে (asymmetric \"core overlap 0.039\" → symmetric 0.159; class-size-weighted \"balanced accuracy 0.894\" → equal-weight 0.625) — ভুল সংখ্যায় কোনো সিদ্ধান্ত নেওয়া হয়নি।

**রায়: KNOWN LIMIT।** কোনো variant বানানো হয়নি (শর্ত ছিল identification আলাদা করলেই removal — করেনি), gate অপরিবর্তিত (p21 stretch-এর কারণে REFUSE থাকে, heading-এর কারণে নয়; heading-এর ৮ শব্দ unrecovered থাকে)। Fitz render চালানো হয়নি — promote করার variant নেই, আর PNG overlap 0.751 একই scan-এর আরেক render-এ separation-এ উল্টে যাওয়ার সম্ভাবনা নেই। **যা দরকার হবে:** word boundary-কে intra-word letter gap থেকে আলাদা করা grouping signal — R22–R24-এ মাপা সব signal (gap width, band width, grey ×6, white-column, run-length, bridge-strength, reservoir, pure-column, transition-count) overlap করে বা উল্টো। সীমানার তথ্য শুধু letter sequence-এই আছে — অর্থাৎ recognition/language জ্ঞান, বর্তমানে নিষিদ্ধ। ব্যবহারকারী recognition-ভিত্তিক grouping ধাপের অনুমতি না দিলে, বা মৌলিকভাবে নতুন signal না পাওয়া গেলে, heading **accepted known limit** হিসেবেই থাকবে।

---

## ৬. T3 চোখ — recall 35/35 (100%) অপরিবর্তিত, কিন্তু gate-এর একটি blind spot মাপা হয়েছে

R23-র Path C চোখ অপরিবর্তিত (recall 35/35 = 100%, ০ false positive); T3 flag ২টি (p20 Path C + p21 Path B) — দুটোই আসল collapse। কিন্তু এই রাউন্ডের দুটি fix ট্র্যাক একটি **আসল blind spot** মেপেছে, যেটা রেকর্ড করা জরুরি:

- **Bridge ট্র্যাক: gate 24/1 (p20 ALLOW) — FALSE।** Bridge p20-র লাইন ৬টি ভুল টুকরো করেছে (0/4 সত্য শব্দ) — তবুও gate ALLOW দিয়েছে, কারণ fused box কাটা হয়ে গেলে T3 চুপ হয়ে যায়, cut সঠিক হোক বা ভুল। **Seam ট্র্যাক: gate 24/1 — FALSE**, একই কারণে (৮ টুকরো, 0/4 সত্য শব্দ)।
- **শিক্ষা: gate collapse ধরে, over-split ধরে না।** একবার fused box ভেঙে গেলে তার টুকরোগুলি T3-র পরীক্ষার জন্য খুব সরু হয়ে যায়। 24/1-এ promote করা হতো R21-র E2 ভুলের পুনরাবৃত্তি — word-identity যাচাই (0/4) সেটা ধরেছে, gate ধরেনি।
- **ভবিষ্যতের জন্য:** gate-এ একটি over-split চোখ দরকার (বা word-identity যাচাই) — নাহলে ভুল cut-ও ALLOW দেখাবে। এটি Round 25-র gate-কাজ (§১০)।

---

## ৭. R23-র শিক্ষা মানা হয়েছে — দুই render-ই যাচাই, E2 অক্ষত

- **দুই render:** bridge/seam ট্র্যাক দুটোই PNG + fitz যাচাই করেছে (১৪টি PG পাতা fitz-এ box-identical, Aug p1 fitz ৩০৮); diagnosis ট্র্যাক p20-তে PNG-vs-fitz **ZERO drift** মেপেছে (byte-identical render, Otsu 217, CC identical)। কোনো \"কিছুই বদলায় না\" দাবি এক render-এ করা হয়নি।
- **E2 অক্ষত:** R21 `_gap_mark` excuse-এর কোনো বদল হয়নি — bridge/seam দুটোই তা বহাল রেখেছে, fitz Aug p1 ৩০৮ ধরে রেখেছে। R23-র E2 removal regression (suite 35/38) এই রাউন্ডে পুনরাবৃত্তি হয়নি।
- **কোনো test expectation বদলানো হয়নি।** কোনো threshold fit করা হয়নি। Suite workspace TMPDIR-এ চালানো হয়েছে (`$HOME/workspace/lse-verify-tmp`), /tmp নয়।

---

## ৮. coverage — 95/97 অপরিবর্তিত

এই রাউন্ডে কোনো misses fix নেওয়া হয়নি — coverage সত্য **95/97** (R23-র সংশোধনসহ), অপরিবর্তিত। বাকি ২টি আসল + ৩টি known-limit miss আগের মতোই: CARRIER NAME লাইন (৮ শব্দ), p21 heading, p21 address লাইন (২৬ শব্দ ১৪ box-এ), p10 \"Prepared\" (geometry-only unfixable), আর stamp fragment-গুলি (সঠিকভাবে drop)।

---

## ৯. সংশোধন (corrections — আগের রিপোর্টের ভুল ঠিক করা)

1. **p21 \"৯ সঠিক / ১৫ ভুল\" → ৮ সঠিক / ১৬ ভুল (১৭ সত্য / ১৯ ভুল cut):** p21stretch ট্র্যাক full-line crop + Otsu-CC structure দিয়ে ২৪টি v2 split আবার যাচাই করেছে — (ক) p01 `[741,…]` **সঠিক ANNAPURNA|TRANSPORT**, \"TRANS|PORT\" নয় (R23-র নিজের `w_p01a.png`-এই দেখা যায়; লেবেলটি p2-র আসল TRAN|SPORT-এর); (খ) p21 `[590,…]` **ভুল correspond|ence** (CC ১৪৫px + ৬০px), \"correspondence|and\" নয়; (গ) p21 `[970,…]` TD/70-|78/… **তালিকাভুক্তই হয়নি, ভুল** (একটি reference token, hyphen-এ ভাঙা)। v2 splitter যেভাবেই হোক DO NOT PROMOTE থাকে।
2. **Omron lead-এর premise বনাম p20diag-র মাপ:** online ট্র্যাকের Top 1 (Omron M) ধরে নিয়েছে সীমানায় bridge-এর কালি stroke-এর চেয়ে হালকা বলে P(x)-এ peak হবে — কিন্তু p20diag মেপেছে p20-র slash **stroke-এর চেয়েও গাঢ়** (bridge ratio 0.99–1.11, min grey 164–183 বনাম gap 201–229)। অর্থাৎ Omron-এর premise p20-র slash-এর ক্ষেত্রে মাপা প্রমাণে **খণ্ডিত** — lead-টি এখনও পরীক্ষিত নয়, কিন্তু তার prior কমে গেছে। p21-র ক্ষেত্রে premise-টি এখনও খোলা (সেখানে dark gap 4px আছে)।
3. **EP0780782 module 14 vote বনাম weak_frac:** module 14-র 10%-নিয়ম (কত ভাগ row-তে bridge) তার নির্ভুল রূপে পরীক্ষিত হয়নি — কিন্তু p21stretch ট্র্যাকের per-row margin মাপ (weak_frac) তার ঘনিষ্ঠ আত্মীয়, আর সেটি কোনো separation দেখায়নি (17/36 = chance)। তাই module 14-র prior-ও কম — তবে নির্ভুল রূপটি (dark-threshold connection fraction + weighted neighbour) Round 25-র পরীক্ষার তালিকায় থাকে।
4. **\"১৪৩টি hidden miss\" → 95/97 (R23-র সংশোধন বহাল):** এই রাউন্ডে নতুন করে কিছু বদলায়নি — সংশোধনটি এখানে পুনরুল্লেখ করা হলো যাতে পুরনো ৯২/৯৭ সংখ্যাটি আর উদ্ধৃত না হয়।

---

## ১০. খোলা বিষয় (open items — Round 25-র জন্য)

1. **p20-র fused লাইন** (`[557,661,986,678]`) — proven known limit। Round 25-র পরীক্ষা (online Top 3-র ক্রমে): (ক) **Omron M** (US 9,710,945 — greyscale min-projection P(x) + fitted line M; p20diag-র মাপ premise-কে দুর্বল করেছে, তবুও সরাসরি পরীক্ষা বাকি); (খ) **skeleton-graph** (US 5,787,196 — skeleton node-ই বলে দেয় কোথায় ভাগ হবে, সংখ্যা না জেনেও); (গ) **tree-indexed demarcation** (Tang 2017 — unreliable valley-কেও tree-তে রেখে width-variation দিয়ে বেছে নেওয়া); (ঘ) **fuzzy vote** (Farulla 2017 — valley গভীরতা + bridge-strength + কেন্দ্র-দূরত্ব, per-page membership)। Separator-glyph ধারণা (diagnosis ট্র্যাকের) আর greyscale-aware re-segmentation — দুটোই unproven, দুটোকেই ১৮টি intra gap-এ no-false-cut যাচাই পাস করতে হবে।
2. **p21-র ৭-শব্দ stretch** — **ACCEPTED KNOWN LIMIT** (§৪)। Round 25-র সিদ্ধান্ত: নতুন discriminator (Omron M / module 14 নির্ভুল রূপ) পরীক্ষা করা, নাহলে limit-টি বহাল রাখা — জোর করে ভাঙা যাবে না। সৎ প্রশ্নটি খোলা থাকে: geometry-only উপায়ে 25/0 কি আদৌ সম্ভব? — এর উত্তর Round 25-র পরীক্ষাগুলি দেবে, অনুমান নয়।
3. **p21 heading** — KNOWN LIMIT (§৫)। Round 25-র পরীক্ষা: **reduced underline** (US 10,586,125 — rule-এর নিজের দীর্ঘ row দিয়ে reduced underline বানিয়ে intersection ফিরিয়ে আনা; R23-র Amazon ব্যর্থতার উল্টো দিক)।
4. **Gate-এর over-split blind spot (§৬):** gate-এ over-split চোখ (বা word-identity যাচাই) যোগ করা — নাহলে ভুল cut-ও ALLOW দেখাবে। Seam ট্র্যাকের process নোট: নতুন split src-কে `_kept_words` whitelist-এ ৩টি one-line hunk দিয়ে যোগ করতে হয় (\"fused-seam\" পরিবার) — ভবিষ্যতের split src-এর জন্য মনে রাখতে হবে।
5. **Knife-edge-গুলো:** F=1.70, FIX3 3px run floor (n=1), floor-4 (genuine-min 77px, window [2,77]) — principled নিয়মে বদলানো যায়নি, মাপা আছে। E2 width boundary এখন আর knife-edge নয় — excuse বহাল আছে।
6. **আগের মতো খোলা:** Virtako label ৫-field decision (user-এর উত্তর অপেক্ষায় — শীঘ্রই আবার জিজ্ঞেস করবে না); Q-03–Q-09, ★2–★8; print calibration (factory printer — শুধু user, Muse-র কাজ শেষে); US patent legal check (lawyer — lead: US 5,734,761 + Adobe US9741142B2 + US 20250111688 + US 20250078557); Windows .exe (Windows-এ build করতে হবে); .docx capture 100/100 (৯৬.৬০% এখন); first-view ~১৪–১৮s।

---

## ১১. যাচাই (verification — parent-এর জন্য)

- **Merge:** `merge-r24/segment_merged.py` + `gate_merged.py` + `rhythm_dp.py` + `logo_detect.py` + `gate_misses.py` + `segs/` (৩৩ পাতা, r23 + r24 দুই set) + `gate_batch_r24_merged.json` + `canon_r24_merged.json` + `merge_segment_r24.py` + `run_segs_r24.py` + `run_gate_r24.py`। ৫টি code ফাইল R23-র সঙ্গে **SHA-256 byte-identical** (merge script-এ যাচাই)।
- **Gate:** 23/2 (২৫ পাতা); ৩১ ALLOW / ২ REFUSE (৩৩ entry)। REFUSE: p20 (T3 Path C, box `[557,661,986,678]`, min_cc_w_med 8.36, fus_cover 0.993) আর p21 (T3 Path B, box `[827,1970,1317,2005]`)। T1 ০, T2 ০। ২৩টি ALLOW পাতার প্রতিটি R23-র সঙ্গে SAME (gate script-এর per-page তুলনা)।
- **শব্দ:** ২৫ পাতা 9373 (=), ৩৩ পাতা 12366 (=); p2 ৬৭৬, p3 ৪৭১; p20 ৫২১ (=), p21 ৫৮৪ (=); PG aug 306/308/305, may 308/313/306 (=)। **৩৩/৩৩ seg byte-identical** (R23 segs-এর সঙ্গে diff খালি)।
- **Canonical:** N5 **41/81** (=), Description ভুল **৩০** (একই list), redbox **7/66** (=), p3 strict **248/384**, improved **285/384**, FP 186, p21 GT **36/42** @ ±5px meet-rule (seam ট্র্যাক স্বাধীনভাবে পুনরুৎপাদন: L1648 7/9, L1926 11/15, L2379 18/18; bridge ট্র্যাকও 36/42), LINES **327/327**।
- **Guard:** **5/5 PASS** (segs byte-identical বলে R23-র ফল অপরিবর্তিত)।
- **DB SHA:** `1c065457bb9cb8e5b276d5007d9b020c18c8a0ae0374b92eb759f12150746939` — আগে ও শেষে একই (DB ছোঁয়া হয়নি)।
- **Fitz render:** Aug p1 **৩০৮ শব্দ**, email ২ শব্দ `[970,417,1080,450]` + `[1122,418,1272,450]`; ১৪টি PG পাতা fitz-এ segment করা হয়েছে (aug 308/308/305/307/303/303/311/309, may 307/313/305/306/305/309)। PNG 306 / fitz 308 — দুই render-পথেই সঠিক।
- **Full suite (repo clone `~/workspace/lse-r24-test/`, lse-r23-test-এর কপি — কোড অপরিবর্তিত):** **38/38 PASS (434.02s, exit 0, 3 warnings)**। Demo **৮২ শব্দ** (নিজে চালিয়ে যাচাই)।
- **Push করা হয়নি, Drive-এ upload করা হয়নি, MEMORY.md ছোঁয়া হয়নি** — parent যাচাই করে push/upload/memory করবে। **Push সিদ্ধান্ত parent-এর:** R24-এ কোনো নতুন code নেই — R24 push করা R23 push করারই সমান (byte-identical)। তাই push-এর প্রশ্নটি R23-রটিই থাকে: R23-কে as-is push করা হবে কিনা (সৎ চোখ + EXP2 উদ্ধারের জন্য), নাকি Round 25 পর্যন্ত রাখা হবে — সেটা reversible working decision হিসেবে parent-এর হাতে।

---

## ১২. উদ্ভাবন বনাম মেরামত (purpose check — ব্যবহারকারীর নির্দেশ)

এই রাউন্ডের **উদ্ভাবন:** তিনটি স্বাধীন **প্রমাণ** (p20diag-র উল্টো-পার্থক্যের টেবিল, bridge/seam-এর word-identity ব্যর্থতা, heading-এ \"নিখুঁত removal-ও 0/8\" — grouping-ই bottleneck) — এগুলি নতুন জ্ঞান, যা ছাড়া Round 25 অন্ধভাবে একই পরীক্ষা আবার করত। আর online research-এর নতুন lead-গুলি (Omron M, skeleton-graph, reduced underline) — প্রতিটি সুনির্দিষ্ট পরীক্ষাসহ। **মেরামত:** কিছুই না — কোনো code বদল হয়নি, কোনো regression ঠিক করতে হয়নি। সৎ মূল্যায়ন: এই রাউন্ড code-এ শূন্য দিয়েছে, কিন্তু **সীমার প্রমাণে** পূর্ণ — আর সীমা না জানলে 100%-র পথে হাঁটা যায় না। সবচেয়ে বড় শিক্ষা: **gate-এর সংখ্যা সত্য নয় — word identity-ই সত্য** (দুটি fix ট্র্যাক 24/1 পেয়েও 0/4 শব্দে ধরা পড়েছে)।
