# LSE Round 20 — রিপোর্ট

**তারিখ:** 2026-11-08 · **ভাষা:** বাংলা · **কো-অর্ডিনেটর:** Round 20 coordinator
**Baseline:** Round 19 merged segmenter + gate (`round19/merge-r19/`, gate 17/8) — read-only, ভাঙা হয়নি
**নতুন baseline:** `improve/round20/merge-r20/` (segment_merged.py + gate_merged.py + segs/)
**ডিরেক্টরি:** `improve/round20/` — প্রতি ট্র্যাকের নিজের ডিরেক্টরিতে তার সব আউটপুট; merge `merge-r20/`-তে

---

## ০. এক নজরে — headline সংখ্যা

| মাপ | R19 baseline | **Round 20 merge** |
|---|---:|---:|
| Gate (২৫ Raviraj পাতা) | 17 ALLOW / 8 REFUSE | **23 ALLOW / 2 REFUSE** |
| ফ্ল্যাগ (T1 / T2) | 16 (9 / 7) | **2 (2 / 0)** |
| মোট শব্দ (২৫ পাতা) | 9012 | 9100 (+88) |
| REFUSE পাতা | p01, p08, p09, p12, p13, p14, p15, p21 | **শুধু p01, p12** |
| Canonical p2 N5 / Description / redbox | 39/81, 39/69, 7/66 | **40/81 (+1), 39/69 (=), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 244 / 285 (181) | **248 (+4) / 285 (=) (186, +5)** |
| Canonical p2 / p3 gate | p2 REFUSE 1/5, p3 ALLOW 0/0 | p2 REFUSE 1/2, p3 ALLOW 0/0 |
| LINES (canonical r15m) | 327/327 | **327/327** |
| PG ৬ পাতা (শব্দ) | aug 306/308/305, may 308/315/308 | **aug 306/308/305, may 308/313/306 — আসল R19 সংখ্যা** |
| p21 GT (৪২ certain boundary) | 33/42 (আসল R19, এই রাউন্ডে মাপা) | **35/42 (+2)** |
| Guard (live page, FULL) | 5/5 | **5/5 PASS** |
| Round 3 DB SHA | `1c065457…` | **`1c065457…` — আগে ও শেষে একই** |

**ফ্লিপ (REFUSE→ALLOW):** p08 (G2 gate-নিয়ম), p09, p13, p14, p15, p21 (dark-core reclaim) — ৬টি পাতা।
১৭টি পুরনো ALLOW পাতার একটিও regress হয়নি। **বাকি ২টি ফ্ল্যাগ:** p01 T1 0.542 (MATA "A"-র core),
p12 T1 0.970 — দুটিই R19-র পুরনো ফ্ল্যাগ।

**Promotion bar-এর রায়: পাস।** ALLOW বেড়েছে (17→23), canonical p2/p3-তে কোনো regression নেই
(LINES 327/327; N5 +1, Description =, redbox =, p3 +4/0), ১৭টি ALLOW পাতা সব ALLOW-ই আছে।
সৎ caveat দুটি: (1) p3 FP 181→186 (+5) — orphan টুকরো GT শব্দের সঙ্গে মেলে না;
(2) p21-এ gate-এর চোখে না-পড়া ৩টি একক অক্ষর এখনো missing (§৯)।

---

## ১. নির্ণয় — নতুন যা পাওয়া গেল (track-diag)

R19-র ১৬টি ফ্ল্যাগের পেছনে কী ছিল, তা আবার চোখে দেখে যাচাই করা হয়েছে (`track-diag/DIAGNOSIS20.md`)।
**১৬/১৬ ফ্ল্যাগ LIVE** (০টি ভুল, ০টি আগেই ঠিক হওয়া) — R19-র নির্ণয় ঠিক ছিল, কিন্তু তিনটি
জায়গায় R19 §৬-র ব্যাখ্যা ভুল প্রমাণিত হয়েছে (§১০ দেখুন)।

**লুকানো miss ১৪৩টি শব্দ** — gate-র ফ্ল্যাগের বাইরে, চোখে দেখে পাওয়া:

| শ্রেণি | সংখ্যা | বিবরণ |
|---|---:|---|
| footer blind spot | 53 | sig_y-র নিচে gate দেখেই না (structural 1D-cutoff বনাম 2D-layout) |
| একক অক্ষর / fragment | 82 | single-CC / T2 blind spot — নিয়মতান্ত্রিক শ্রেণি |
| p21-র গোটা heading লাইন | 8 | huge-blob filter খেয়ে ফেলে (fill 0.65 বনাম table ≤0.08) |
| **মোট** | **143** | প্রতি পাতা: p01 25, p08 2, p09 1, p12 2, p13 19, p14 19, p15 19, p21 56 |

**নতুন নিয়মতান্ত্রিক mechanism (নাম দেওয়া হয়েছে):**
1. **dark-threshold blindness** — validator শুধু dark ink (<119) পরীক্ষা করে; ধূসর অক্ষর (grey 120–140) দেখে না।
2. **sig_y footer blind spot** — gate-র 1D sig_y cutoff footer-কে কাঠামোগতভাবে বাদ দেয়।
3. **single-CC / T2 blind spot** — T2-তে n_cc≥2 লাগে; একা ১টি CC-র অক্ষর gate-র চোখে পড়ে না।
4. **huge-blob filter** — fill বেশি হলে blob বাদ যায়; p21-র heading লাইন এভাবেই হারিয়েছিল।

dbnet Signal B-ও ০টি নতুন miss পেয়েছে (এই ১৪৩টির বাইরে) — detector-র চোখেও এগুলো ধরা পড়ে না,
কারণ সমস্যাটা detector-এ নয়, নিয়মে (§৮)। gap-band ১১টি pair চোখে দেখা হয়েছে, ০টি split
(৯৪-র মধ্যে ৮৩টি অযাচাইকৃত — দাবি করা হয়নি)।

---

## ২. track-online — গবেষণা (RESEARCH20.md, ৭৫৫ লাইন)

**ফল: NO HIT।** ৪৭টি R-নম্বর, ৪৬টি এন্ট্রিতে (R39/R39b আলাদা; ফাঁক R12, R16, R40, R47);
§৩ shortlist ৫১টি row। LSE-র পূর্ণ সংমিশ্রণ (scan-ই পাতা + শব্দ-স্তর segmentation, OCR ছাড়া +
inpainting + retype + 100% originality) কোথাও পাওয়া যায়নি — না প্রোডাক্টে, না স্টার্টআপে,
না ওপেন-সোর্সে, না পেটেন্টে।

**৩টি নতুন LEAD (আইনজীবীর কাছে যাবে — কোনো verdict নয়, claims পড়া হয়নি):**
- US 20250111688 (patent APPLICATION), US 20250078557 (patent APPLICATION) — দুটোই আবেদন, claims অ-পড়া।
- Scanned.To — বাণিজ্যিক VLM cloud converter (conversion, preservation নয় — LSE-র উল্টো দিক)।

**সংশোধিত dbnet test-ক্রম (প্রস্তাব, R19 §১১-র বদলে):** tiny → small → MBG-PSENet → DBNet++ →
SMNet → CRAFT শেষে; medium বাদ (২.৯২ s/পাতা — ২ সেকেন্ড bar-এর উপরে)। dbnet ট্র্যাক এই
সংশোধিত ক্রমই অনুসরণ করেছে (§৮)।

**সতর্কতা (গুরুত্বপূর্ণ):** "no OCR" স্লোগান এখন বাণিজ্যিক marketing — LSE-র দাবি সঠিকভাবে বলতে
হবে: **"no recognition at all — neither OCR nor VLM; geometry only"** (কোনো recognition-ই নয় —
OCR-ও নয়, VLM-ও নয়; শুধু geometry)।

---

## ৩. track-frag — small-fragment rescue "es" (PROMOTE — standalone; merge-এ subsumed)

**Standalone ফল: gate 17/8 → 20/5** (কো-অর্ডিনেটরের নিজের যাচাই: `gate_batch_frag.json` সরাসরি
পড়ে 20 ALLOW / 5 REFUSE; নতুন ALLOW p13, p14, p15; p01 T2 cleared, তবু ২টি T1-এ REFUSE;
p21 T2 3→1; ১৭টি ALLOW অপরিবর্তিত; শব্দ সংখ্যা অপরিবর্তিত; T1max অভিন্ন)। Canonical p2 N5 39/81,
Description 39/69, redbox 7/66 অভিন্ন; **p2 gate REFUSE (1/5) → ALLOW (0/0)**; p3 244/285
অভিন্ন; LINES 327/327; PG ৬/৬ অভিন্ন; false-add ০, false-remove ০; ১২টি rescue চোখে যাচাই করা
(৫টি গোটা শব্দ: "packages"×৩, "Caution", "preparing"); ১টি সঠিকভাবে প্রত্যাখ্যান (p21-র standalone
"of" — জোড়া লাগালে দুটি আসল শব্দ ভুলভাবে merge হতো)।

**মূল কারণ:** blob-split-এর dark-ink sub-দের area floor 34; "es"-এর dark টুকরোর সর্বোচ্চ area 33 —
১ কম বলে বাদ যেত। **Fix:** post-hoc Otsu gap-attach (extension only — শব্দ সংখ্যা কখনো বদলায় না):
uncovered word-like cluster পাশের একই লাইনের শব্দের বাক্স বাড়িয়ে ঢাকে।

**Merge-এ ভূমিকা:** reclaim2c-র ওপরে gap-attach চালিয়ে মাপা হয়েছে (`merge-r20/apply_frag_attach.py`) —
**২৫ পাতায় ০টি rescue** (শুধু canonical p2-তে ২টি — §৯ দেখুন)। অর্থাৎ frag-এর gate-মূল্য
reclaim2c-র ভেতরে পুরোপুরি subsumed; merge segmenter-এ gap-attach ঢোকানো হয়নি (অপ্রয়োজনীয় জটিলতা
বাড়াত)। Mechanism-টি সঠিক ও নির্দোষ প্রমাণিত — Round 21-এ p2-র ২টি rescue-র জন্য integration-এর
প্রার্থী। উদ্ভাবন-বিচার: **মেরামত, আবিষ্কার নয়** (সৎভাবে বলা হয়েছে)।

**সংশোধন:** R19 §৬-র p01 T2 "perforation-dot column, JUNK" **ভুল** — ওটা "SC" of "SCHEDULE",
আসল text; কোনো perforation exclusion implement করা হয়নি (আসল text লুকিয়ে ফেলত)।

---

## ৪. track-p01 — logo-rect ডান কিনারা (DO NOT PROMOTE)

**ফল: gate 17/25 → 11/25 (REGRESSION)।** Baseline নিখুঁতভাবে reproduce করা হয়েছে (৩৩ পাতা,
১১,৯৫৯ শব্দ, ০ diff, 17/8)। Candidate (page-adaptive right-edge extension): ফ্ল্যাগ ১৬ → ৩১
(৮+২৩); p01 REFUSE-ই থাকে (1/1); **ছয়টি ALLOW পাতা p22–p27 REFUSE-এ উল্টে যায়**।

**ভিত্তিটাই ভুল ছিল:** কোনো "A"-leg নেই — T1a core [900,275,934,311] হলো tagline **"Nothing's"-এর
"N"** (geometry: শেষ MATA "A" x=840-এ শেষ, 850-এ শেষ হওয়া rect আগে থেকেই ঠিক ছিল; colour: core
tagline-নীল BGR [155.9,131.2,111.6], MATA "A" সবুজ-প্রধান; connectivity: core N-এর নিজের Otsu
CC (898,271,936,315)-এর dark অংশ)। x=934 পর্যন্ত যাওয়া rect আসল text গিলে ফেলে (p22–p27 header-এর
প্রথম অক্ষর হারায়: "NDIAN", "ENTRAL"…)।

**T1a-র আসল কারণ:** row-split 1px limit (tagline blob h=61 বনাম 3·med_h=60 → ভুল row cut →
F3 overlap-drop ওপরের শব্দ [901,275,1061,303] মারে, overlap 2312 বনাম 2240, ৩% margin) —
row-split owner-এর কাছে handoff। T1b "SCHEDULE" নির্ণয় করা হয়েছে (dark threshold বেশি dark,
median grey ~145; _group_subs gap 31-এ কাটে বনাম threshold 30, ১px margin; subcov==1.0 grey<140
core-র প্রতি অন্ধ) — v3gate/top2a-র কাছে handoff। Canonical p2 631→620 শব্দ (−১১), N5 39→40,
Description 39/69, redbox 7/66, gate REFUSE (1/5) অপরিবর্তিত; p3 অভিন্ন; LINES 327/327; PG অভিন্ন।

---

## ৫. track-v3gate — v3 gate test (KEEP — threshold বদলে gate বদলায় না)

Threshold 6.0 / 5.0 / 4.0 — **তিনটিতেই 17/8, একই REFUSE তালিকা** (কো-অর্ডিনেটরের নিজের যাচাই:
তিনটি gate JSON সরাসরি পড়া হয়েছে); T1 শুধু বাড়ে (9→10→13); শব্দ 9012→9161→9242। Target blob-গুলো
gate-র ওপরেই আছে (PACKFIRM ~6.7×, SCHEDULE ~9.3×, ORIGIN 6.67×) — threshold কমিয়ে সেগুলো বদলানো
যায় না; আসল ভুল split tightness-এ (subcov পাস করে, কিন্তু একটি letter core বাক্সের বাইরে থাকে)।

Over-split চোখে যাচাই করা: 5.0-র নমুনা 72 → ৫১টি ভুল (৭১%); 4.0-র নতুন নমুনা 66 → ৩৯টি ভুল (৫৯%)।
নতুন ক্ষতি: p09-এ 5.0-তে T1 1→2 ("LIMITED." → "LIMIT"+"ED."); p13/14/15-এ 4.0-তে T1 0→1 প্রতিটি
("declare"→"decl"+"are")। DP-র নতুন firing শুধু digit string টুকরো করে (p11 "0002571", p09 "8514561"
→ ৬টি digit-box প্রতিটি)। Canonical p2 N5 39→39→40, Description 39, redbox 7, gate REFUSE 1/5
তিনটিতেই; p3 strict 244→248→245, improved 285→288→283, FP 181→192→203, gate ALLOW; LINES 327/327।
**CONDITIONAL-ও নয়** — সঠিক বনাম ভুল split আলাদা করার কোনো মাপা শর্ত পাওয়া যায়নি।

---

## ৬. track-gateside — gate-side T1 assignment (G2 PROMOTE; v4 নয়; v3 REJECTED)

**G2 (line-band majority rule) PROMOTES: 17→18, শূন্য seg পরিবর্তন, ৩৩ পাতায় ঠিক ১টি suppression**
(চোখে যাচাই করা নীল signature stroke)। নিয়ম (নতুন magic number নেই — majority, 0.50): core-র
pixel-দের >50% তার শব্দের line-band-এর বাইরে থাকলেই T1 suppress হয়। সব আসল T1 kept।

Cross-attribution (কো-অর্ডিনেটরের নিজের re-run): **A (v4 seg + merged gate) = 17/8** (p12 ঠিক,
p10 ভাঙা — net ০); **B (G2 gate + merged seg) = 18/7** (শুধু p08 ফ্লিপ, band_supp=1, বাকি সব
অপরিবর্তিত); **combined (G2+v4) = 18/7 কিন্তু p10 ALLOW→REFUSE** (নতুন false T1, 1px touch) —
bar মেটে না।

**v4 injection PROMOTE নয়:** surgical (huge CC-র mask-এর ভেতরের নীল pixel মুছে CC আবার চালানো,
print-like fragment inject করা) আসল অক্ষর ঠিক করে (P, B, "red", "d", y-tail, "PLC)") আর p12 ঠিক
করে, কিন্তু p10 ভাঙে, p09 "Prepared" ১→৩ টুকরো করে, p12 "Approved"-এ near-miss রাখে (0.455)।
**v3 (গোটা image blue-whitening) REJECTED** — Otsu threshold নষ্ট করে, নীল print ধ্বংস করে।
Canonical + PG অভিন্ন; LINES 327/327।

---

## ৭. track-top2b — DP বনাম DBNet reconcile, DNA ligature veto, min-cut (NO promotion, NO regression)

p21-র boundary **42/42 নিশ্চিত**; ২টি ভুল cut (L2012 @578, L1370 @621) অপরিবর্তিত। Gate top2b frame
11/25 (ঠিক R19 top2b, R19-র gate ফাইলের সঙ্গে মিলিয়ে যাচাই করা); merged frame 17/8 (R19 merged-এর
সঙ্গে ০/২৫ verdict mismatch); merged+reconcile-ও 17/25; no-DP control-ও 17/25। Canonical p2 N5
18→21, Description 7/69, redbox 7/66; p3 strict 240/384, improved 280/384 — সবই ঠিক R19 top2b;
LINES-চেক বনাম raw: removed 21 / added 38, false_new ০।

**তিনটি পরীক্ষাই NEGATIVE:**
1. **reconcile:** agreement 96.5% (2169/2248 লাইন), ৭৯টি disagreement সব dp>class (+343 শব্দ),
   ink mediation dp=28/class=1, R1-final firing ০ (নিরাপদ কিন্তু নিষ্ক্রিয়)।
2. **DNA ligature veto:** ৩টি ভুল cut-এর ০টি block করে, আর ৪–৫/৪২ আসল cut হারায় (IoU 0.65) /
   ৭–১০/৪২ (0.55) — integrate করা হয়নি, rhythm_dp.py byte-identical R19-র সঙ্গে। Hypothesis ভুল
   (একই glyph-pair শব্দের ভেতরে AND boundary-তেও আসে; ভুল cut-গুলো শূন্য ink পার হয়, ligature নয়)।
3. **min-cut:** ২৫২টি cut-এর ০টি ink পার হয়, ২টি আসল italic লাইন কিন্তু কোনো vertical-cut failure
   নেই — বানানো হয়নি।

**গভীরতর ফল:** ২টি ভুল cut DP-র জন্য FLOOR — shape একা ঠিক করতে পারে না (নিশ্চিত-boundary gap ৪–৮px,
ভুল-cut gap-ও ৪px/৮px; ink, DBNet আর DNA সবাই DP-র পক্ষে বা নীরব; পার্থক্যটা শব্দের অর্থে, যা no-OCR-এ
পাওয়া যায় না)। পরের ধাপের প্রার্থী (সিদ্ধান্ত নয়): L98 "DP rescue for non-singleton merged lines"।

---

## ৮. track-dbnet — detector মডেল-টেস্ট (tiny PROMOTE; বাধা detector নয়, prompt-নিয়ম)

R19 §১১-র ক্রমের বদলে অনলাইন-ট্র্যাকের **সংশোধিত ক্রম** অনুসরণ করা হয়েছে (tiny → small → MBG-PSENet →
DBNet++ → SMNet → CRAFT; medium বাদ, EAST বাদ)। Ground truth: ১৬টি merged-gate flag (gate JSON থেকে
সরাসরি গুনে মিলিয়েছি: ১৬), Raviraj লুকানো miss ১টি (p21), canonical PG লুকানো ১২টি।

| মডেল (copy1080, D10) | Flag (prompt) | লাইন-ঢাকা | লুকানো (Rav) | Canon লুকানো (PG) | সময় (quiet median) | ২s bar |
|---|---:|---:|---:|---:|---:|---|
| **PP-OCRv6 det tiny** | **7/16** | **16/16** | 0/1 | 12/12 | **607 ms** | ✅ 16/16 |
| PP-OCRv6 det small | 7/16 | 16/16 | 0/1 | 12/12 | 1,265 ms | ✅ 15/16 |
| PP-OCRv5 (control) | 7/16 | 16/16 | 0/1 | 12/12 | 4,214 ms (R19, busy) | ❌ অপ্রমাণিত |
| DBNet++ RepViT | 4/16 | 13/16 | 0/1 | 12/12 | 1,641 ms | ✅ 16/16 |
| CRAFT | 7/16 | 14/16 | 0/1 | 12/12 | 20,192 ms | ❌ 0/16 |
| tiny + threshold tuning (৪ variant) | 7/16 | 16/16 (bt07: 15/16) | 0/1 | 12/12 | — | — |

(কো-অর্ডিনেটরের নিজের যাচাই: eval JSON-গুলো সরাসরি পড়ে মোট মিলিয়েছি — tiny 7/16, line 16/16;
DBNet++ 4/16, line 13/16; CRAFT 7/16, line 14/16; snapshot-পুনঃমাপেও একই।)

**সবচেয়ে বড় আবিষ্কার: flag ধরা 7/16-এ আটকে আছে — মডেল বদলালেও নড়ে না।** tiny, small, v5,
fullres, copy1080, threshold টিউনিং — সবাই একই 7/16 দেয়। আর লাইন-ঢাকা 16/16 — detector সব
flag-এর লাইন **দেখে**, কিন্তু Signal B-র prompt-নিয়ম মাত্র ৭টিকে prompt বানায়। **বাধা detector নয়,
prompt-নিয়ম।** ৯টি missed flag-এর নির্ণয়: ২টিতে uncovered-CC cluster-ই নেই (seg-শব্দ ঢেকে রেখেছে),
৭টি একক-CC cluster (n_cc=1 → wordlike নিয়মে বাদ)।

**সুপারিশ:** **PP-OCRv6 det tiny (copy1080) PROMOTE** — v5-র বদলে Signal B লাইন-oracle হিসেবে
(1.9 MB, quiet-এ 607 ms — R19-এ অপ্রমাণিত ২ সেকেন্ড bar এবার মাপা সত্যে মিটেছে)। small নেবেন না
(২× ধীর, শূন্য লাভ)। DBNet++ নেবেন না (13/16, চীনা-টেক্সটে ট্রেইন করা, p13/14/15-র একই "es"
টুকরো হারায়)। CRAFT নেবেন না (কভারেজে লাভ নেই, সময় ১০–২৩× বেশি)। Tuning-এ লাভ নেই — 0.5/1.6
রাখুন। **নতুন ভূমিকার প্রস্তাব (সিদ্ধান্ত নয়):** detector-কে একক-CC টুকরোর "সাক্ষী" হিসেবে ব্যবহার,
বা সরাসরি লাইন-oracle (16/16) — এটাই এই ট্র্যাকের উদ্ভাবন-প্রস্তাব। MBG-PSENet থেমেছে (কোড/ওজন নেই —
GitHub ০, শুধু পেপার); SMNet পরীক্ষা হয়নি (detector বাধা নয় বলে প্রমাণিত হওয়ায়)। ভুল-শনাক্তকরণ
চোখে ≈2% (p01/aug-p1 overlay)।

**GT সংশোধন-নোট — rav-p2-তে ৫টি নতুন আসল miss:** "CY" (AGENCY), "17." (AADCM0917.A), "o" (Caution),
"BH" (BHULTA), "ou" (Amount) — সব মডেল ৫টিই ধরে। GT ফাইল নীরবে বদলানো হয়নি; merged-baseline-এ
p2-র আসল লুকানো miss **০ নয়, ৫**। পরের রাউন্ডে GT-তে যোগ করার সিদ্ধান্ত gate-ট্র্যাকের।
এর মধ্যে ২টি ("CY", "BH") frag gap-attach merge segs-এ ঢেকে দেয় (§৯) — দুই ট্র্যাকের স্বাধীন
নিশ্চিতকরণ।

**সময়ের সতর্কতা:** busy-সংখ্যা মেশিনের, মডেলের নয় (load ৩০-এ tiny ৪.৮ s, load ০.৯-এ ০.৮ s —
একই পাতা)। R19-র v5-সংখ্যা (৪,২১৪ ms, load ৩.৩–৮.২) আর এই রাউন্ডের quiet-সংখ্যা সরাসরি তুলনীয়
নয়; v5-র quiet-মাপ এই রাউন্ডে করা হয়নি। "Quiet" ব্যাচটিও পুরোপুরি নীরব ছিল না (load ০.৫–৯.৪) —
এগুলো quiet-ish মাপ, isolated-মেশিনের মাপ নয়।

---

## ৯. track-p21 — p21 + adaptive dark threshold + composition (reclaim2c PROMOTE)

**সুপারিশ: `reclaim2c` (dark-core reclaim v2c, gap floor ছাড়া) — R19 merged segmenter-এর জায়গায়
নতুন baseline।** Merge-এ এটাই নেওয়া হয়েছে (§১১)।

| মাপ | R19 baseline (A) | reclaim2c |
|---|---|---|
| Gate (২৫ পাতা) | 17/8, ফ্ল্যাগ 16 (T1 9, T2 7) | **22/3, ফ্ল্যাগ 3 (T1 3, T2 0)** |
| p21 | REFUSE, 4 T1 + 3 T2, 543 শব্দ | **ALLOW, 0/0, 563 শব্দ** |
| Canonical p2 N5 / Description / redbox | 39/81, 39/69, 7/66 | **40/81 (+1), 39/69 (=), 7/66 (=)** |
| Canonical p3 strict / improved (FP) | 244 / 285 (181) | **248 (+4) / 285 (=) (186, +5)** |
| Canonical p2/p3 gate | p2 REFUSE 1/5, p3 ALLOW 0/0 | p2 REFUSE 1/2, p3 ALLOW 0/0 |
| LINES | 327/327 | **327/327** |
| ১৭টি ALLOW পাতা | — | **সব ALLOW-ই আছে** |
| PG ৬ পাতা | aug 306/308/305, may 308/315/308 | aug 306/308/305, may 308/315/308 (stale-base সংখ্যা — §১১ দেখুন) |

(কো-অর্ডিনেটরের নিজের যাচাই: `gate_batch_reclaim2c.json` সরাসরি পড়ে 22 ALLOW / 3 REFUSE,
T1 3, T2 0, শব্দ 9100 — মিলেছে; p21 GT scorer নিজে চালিয়ে 35/42 — মিলেছে।)

**p21-র ৭টি ফ্ল্যাগের আসল কারণ (চোখে যাচাই করা):** ৪টি T1-এর core-গুলোর mean gray ~144–153,
frac<140 ~0.45–0.52 — অক্ষরগুলো ধূসর (grey 120–140), gate-র core (<140) আছে কিন্তু dark sub
(<119) নেই। **dark-threshold fragmentation: হালকা অক্ষরের কোনো dark sub থাকে না, তাই subcov
সেটা ধরতে পারে না।** dark=140 দিয়ে grouping করা মাপা ভুল (blob [1693,1569,2028,1600]-এ ৪টি গ্রুপ
১টিতে bridge হয়; "from"+"any" এক গ্রুপে জোড়া লাগে)। **দুটি threshold-এর ফাঁকটাই সমস্যা:**
pipeline দেখে dark (<119), gate দেখে core (<140); অক্ষরের dark core আর হালকা halo-র মাঝখানে যা
থাকে, সেটাই clip হয়।

**নকশা — dark-core reclaim (`_reclaim_core`, CORE_THR=140):** dark grouping-এর জন্য 119-ই থাকে;
140-sub শুধু grouping-এর *পরে* coverage-চেক হিসেবে ব্যবহৃত হয়: (1) 140-sub ঠিক **একটি** word
box-কে overlap করলে বাক্সটি বাড়ানো হয় (T1 clip ঠিক হয়); (2) **দুই বা ততোধিক** বাক্স overlap
করলে ছেড়ে দেওয়া হয় (কাটার ওপর bridge — অনুমান নয়); (3) **কোনো** বাক্স overlap না করলে সেটি
নিজেই `src=core-reclaim` word box হয়, যদি word-like হয়। **গুরুত্বপূর্ণ শর্ত — reclaim শুধু
validated split-এর পরে চলে** (আগে চালালে মেপে ব্যাকফায়ার করে: খারাপ eroded split reclaim-এর
coverage-প্যাচে subcov পাস করে ফেলে)।

**Composition (৮টি রূপ মাপা হয়েছে):** DP-first (top2b-first) p21-এ নিখুঁত (GT 42/42, ০ ভুল cut)
**কিন্তু প্রত্যাখ্যান** — দাম: Description 39→32 (−৭), p3 strict 244→218 (−২৬), improved 285→258
(−২৭), FP 181→290 (+109), PG Aug-এ +107 শব্দ/পাতা (over-split), ২৫ পাতায় +1714 শব্দ, seg 634.4s।
**Floor-এর রায়: শুধু ক্ষতি, কোনো লাভ নেই** (floor-only gate 17/8 — ফ্ল্যাগ একটাও বদলায় না; মোট
−১৬৯ শব্দ; N5 39→38, Description 39→37)। **v2b fix:** "g"-র descender — 140-তে "g" তিন টুকরোয়
ভাঙে, orphan শুধু bowl নিত, descender বাইরে থেকে T1 0.505 তৈরি করত (আসল বাধা height floor
0.4×med_h, area floor নয়); core sub-দের জন্য area_floor 34→20 **এবং** h_floor 0.4→0.25, orphan
clustering 2D। **v2c fix (নীতিগত):** orphan হলো fragment, শব্দ নয় — whole box বদলানোর ভোটে তার
গণনা চলে না (p01-এ "Hi-Tech" আর ইমেইল "matapltd@matagroup.in" ফিরে এলো)।

**কোন পাতা ফ্লিপ করল (v2c বনাম base):** p09, p13, p14, p15, p21 — REFUSE→ALLOW। p01 উন্নত
(2/1→1/0)। **বাকি ৩টি ফ্ল্যাগ:** p01 T1 (MATA 0.542), p08 T1 (0.886), p12 T1 (0.970)।

**Gate-র অন্ধ জায়গা — ink coverage:** gate-র T2-তে n_cc≥2 লাগে — একা ১টি CC-র অক্ষর gate দেখে না।
স্বাধীন coverage-চেক (letter-like CC যার কেন্দ্র কোনো word box-এ নেই): base ৩২ → reclaim2c **৬**
(dpfirst ৩)। ৬টির মধ্যে ৩টি আসল একক অক্ষর এখনো missing ("i", "l", "ability"-র "l") — bridged/light-letter
কেস; **সৎ সীমা: gate 0/0 মানেই প্রতিটি অক্ষর covered নয়।** ভবিষ্যতের আসল দিক (এই ট্র্যাকে বানানো
হয়নি): **gap-aware DP** — DP-র cost-এ word-gap-এর ওজন, যাতে সে শুধু আসল word gap-এই কাটে।

**সময়ের সতর্কতা:** মেশিন ৪ CPU; রানগুলোর সময় loadavg ০.৪–২৪.৬ পর্যন্ত ওঠানামা করেছে (সমান্তরাল
ট্র্যাক চলছিল; ~০৯:১০-এ VM reboot হয়ে প্রথম `run_all.sh` মারা যায়, আবার চালানো হয়)। seg/gate-র
সেকেন্ডগুলো load-দূষিত — শুধু dpfirst-এর seg (634.4s) নিশ্চিতভাবে ধীর। reclaim2c-র seg গড়
3.96s/পাতা, সর্বোচ্চ 6.7s।

---

## ১০. যাচাইয়ে ধরা সংশোধন (corrections caught in verification)

Round 20-র সবচেয়ে মূল্যবান অংশ হয়তো এটাই — নিজের আগের ভুলগুলো মেপে ধরা পড়েছে:

1. **R19 §৬-র p01 T2 "perforation-dot column, JUNK" ভুল** — ওটা "SC" of "SCHEDULE", আসল text
   (track-frag + track-diag, দুজনেই স্বাধীনভাবে)। কোনো perforation exclusion করা হয়নি।
2. **R19 §৬-র p01 T1a "logo-rect A-leg" ভুল** — core হলো tagline "Nothing's"-এর "N", logo "A" নয়
   (track-p01: geometry + colour + connectivity — তিনভাবে প্রমাণিত)। T1a-র আসল কারণ row-split 1px limit।
3. **R19 §৬-র F01/F03/F11 ভুল** (track-diag): F01 mechanism — logo-rect ভুল; F03 — "SC" আসল text,
   perforation ভুল; F11 word — "from", "in" নয়। p13-র label-ও সংশোধন করা হয়েছে।
4. **p21 ট্র্যাকের "baseline byte-identical" দাবি ভুল** (কো-অর্ডিনেটরের যাচাই): `segment_base.py`
   আসল R19 segmenter-এর সঙ্গে byte-identical নয় — R19-র দুটি fix অনুপস্থিত (eroded positive-gap
   median; subcov `== 1.0` বনাম `>= 0.92`)। **সব R20 ট্র্যাকের segmenter-ই pre-fix কপি থেকে বানানো**
   (frag, gateside, v3gate, top2b, p21 — সবগুলোতে `>= 0.92` নেই)। এর ফল: p21-র segs-base-এ
   may-p2/may-p3 শব্দ 315/308 (আসল R19: 313/306 — R19 segmenter নিজে চালিয়ে যাচাই করা হয়েছে)।
   Merge-এ দুটি fix-ই পুনরুদ্ধার করা হয়েছে (§১১)।
5. **Round 11-র ভুল সংখ্যা (R19 থেকে বয়ে আসা):** 80.9% (643/795) ভুল ছিল — আসল denominator 886,
   আসল মান 70.9% (628/886)। এই রাউন্ডে সব canonical সংখ্যা scorer দিয়ে আবার মাপা হয়েছে।
6. **dbnet ট্র্যাকের দুটি ঘটনা (সৎভাবে লেখা):** (a) tune-ব্যাচ একবার v6-baseline মুছে ফেলেছিল —
   ধরা পড়ে ঠিক করা হয়েছে, baseline নতুন করে বানিয়ে লাইন-সংখ্যা মিলিয়েছি (140/82); (b) অন্য একটি
   Round 20 ট্র্যাক eval-চলাকালীন `merge-r19/segs/` পুনর্লিখন করছিল (p21: 543→538→543) — segs স্থির
   হওয়ার পর snapshot নিয়ে **১১টি eval আবার চালানো হয়েছে, সব মোট হুবহু মিলেছে**।
   বর্তমান অবস্থা যাচাই করা হয়েছে: `merge-r19/segs/` R19 gate JSON-এর সঙ্গে ২৫ পাতায় ০ mismatch;
   may-p2/may-p3 আসল R19 সংখ্যায় (313/306) ফিরে আছে।
7. **p21 GT-র আসল R19 মান:** R19 segmenter নিজে চালিয়ে মাপা হয়েছে — **33/42** (stale-base-ও 33/42
   দেয়, কাকতালীয়ভাবে)। reclaim2c 35/42 — R19-র চেয়ে +২, শুধু gate-এ নয়, identity-তেও উন্নতি।
8. **Live পাতা অপরিবর্তিত:** Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2
   `539995a9…`, May p3 `8587be86…` — R11 থেকে একই; root পাতা canonical, কখনো re-promote নয়।
9. **`round18/merge-r18/verdicts-r15m.json`-এর mtime সেশনে দুবার বদলেছে** (p21 ট্র্যাকের পর্যবেক্ষণ) —
   অন্য কোনো ট্র্যাক/agent লিখছে বলে মনে হয়। LINES rescorer তার নিজের check-গুলো (CHARGES
   byte-identical, diff == expected 6/4) পাস করে 327/327 দিয়েছে, তাই content প্রত্যাশিত অবস্থায় আছে।
   এই রাউন্ডে LINES আবার চালিয়ে 327/327 নিশ্চিত করা হয়েছে।

---

## ১১. Merge — reclaim2c + G2 = 23/2 (কো-অর্ডিনেটরের নিজের কাজ)

**উপাদান:** reclaim2c segmenter (track-p21, standalone 22/3) + G2 gate-নিয়ম (track-gateside,
standalone 18/7)। frag gap-attach merge-এ নেওয়া হয়নি — ২৫ পাতায় ০ rescue, subsumed (§৩)।

**Merge-র যাচাই (কো-অর্ডিনেটর নিজে চালিয়েছে, track-দের সংখ্যা বিশ্বাস করে নয়):**
- Gate নিজে চালানো: **23/2, T1 2, T2 0** — p08-এ ঠিক ১টি G2 suppression (core [1934,2460,1983,2511],
  above_band 0.897 — নীল signature stroke); p01 1/0, p12 1/0; ১৭টি পুরনো ALLOW সব ALLOW।
- Canonical নিজে চালানো: N5 **40/81**, Description **39/69**, redbox **7/66**, p3 strict **248/384**,
  improved **285/384**, FP 186; p2 gate REFUSE 1/2, p3 ALLOW 0/0; PG শব্দ আসল R19 সংখ্যা।
- p21 GT scorer নিজে চালানো: **35/42** (আগের ১০টি ভুল cut-ই একই)।
- LINES rescorer নিজে চালানো: **327/327**। Guard FULL নিজে চালানো: **5/5 PASS**।
- Round 3 DB SHA আগে ও শেষে একই: `1c065457bb9c…`।

**Merge-এ ধরা দুটি গুরুতর সমস্যা (এই রাউন্ডের আসল যাচাই-মূল্য):**

**(a) R19-র দুটি fix অনুপস্থিত ছিল** — সব R20 ট্র্যাক pre-fix কপি থেকে বানানো (§১০.৪)। Merge-এ
দুটি fix পুনরুদ্ধার করা হয়েছে (eroded positive-gap median; subcov `>= 0.92`) আর ৩৩ পাতা আবার
segment করা হয়েছে। ফল: may-p2/may-p3 আসল R19 সংখ্যায় ফিরেছে (313/306), gate 23/2 অপরিবর্তিত।

**(b) `rhythm_dp.py` অনুপস্থিত ছিল — আর gate সেটা ধরতে পারেনি।** প্রথম fixed merge-র gate-ও 23/2
দিয়েছিল, কিন্তু p21 GT 35/42 → **17/42**-এ ভেঙে পড়েছিল: L2379 গোটা লাইন (১৯ শব্দ) ১টি বাক্সে
[555,2379,2028,2419] collapse করেছিল। কারণ: `merge-r20/`-তে `rhythm_dp.py` কপি করা হয়নি —
segmenter import silently fail করে (`try/except` → `_rhythm_dp_words = None`) আর DP কখনো চলে না;
top2a-তে fail করা blob-গুলো whole box হিসেবে থেকে যায়। **Gate এই শ্রেণির failure-র প্রতি অন্ধ**
(একটি বড় বাক্সে কোনো uncovered cluster নেই, কোনো T1 নেই) — শুধু p21 GT scorer-ই ধরেছে।
`rhythm_dp.py` যোগ করার পর (R19-র সঙ্গে byte-identical যাচাই করা) p21 GT 35/42-এ ফিরেছে, gate
23/2 অপরিবর্তিত। **শিক্ষা:** segmenter ডিরেক্টরিতে `rhythm_dp.py` + `logo_detect.py` না থাকলে
import নীরবে fail করে — ভবিষ্যতে segmenter চালানোর সময় DP সক্রিয় কি না, তা log-এ যাচাই করতে হবে
("rhythm-dp blob" লাইন আছে কি না); আর gate-কে whole-line collapse ধরার চোখ দিতে হবে (§১৪)।
ভুল ablation-ও ধরা পড়েছে: /tmp-তে করা variant-পরীক্ষাগুলোতেও rhythm_dp.py ছিল না, তাই সেগুলোর
ফল (দুটি fix-ই আলাদাভাবে collapse ঘটায়) **অবৈধ** — আসল কারণ missing ফাইল, fix-গুলো নয়।

**সময় (loadavg সহ):** merge seg ৮৪.৯s / ৩৩ পাতা (গড় ২.৬s/পাতা, load ০.৯৮–১.৮৫);
gate ৯৫.৩s / ৩৩ পাতা। এগুলো busy-VM মাপ, isolated-মেশিনের নয়।

**নতুন baseline:** `merge-r20/segment_merged.py` (R19 fixes + reclaim2c) + `merge-r20/gate_merged.py`
(R19 gate + G2) + `merge-r20/segs/` (৩৩ পাতা)। পুরনো audit trail `segs-prefixed/` (pre-fix reclaim2c),
`segs-nodp/` (rhythm_dp ছাড়া fixed run — ভুল প্রমাণিত), `gate_batch_r20_prefixed/nodp.json`-এ রাখা আছে।
**নোট:** public GitHub repo-তে এখনো Round 18-র কোড (commit 93bab61e) — Round 19-র push আলাদা worker-এর
কাজ; Round 20 merge-র push সিদ্ধান্ত parent-এর (এই রিপোর্টে সিদ্ধান্ত নেওয়া হয়নি)।

---

## ১২. উদ্ভাবন-বিচার (purpose test — সৎভাবে)

ব্যবহারকারীর স্থায়ী নির্দেশ: শুধু মেরামত নয় — **উদ্ভাবনী প্রযুক্তি** হতে হবে। প্রতি ট্র্যাকের রায়:

| ট্র্যাক | রায় |
|---|---|
| online গবেষণা | জ্ঞান-ভিত্তি; নিজে উদ্ভাবন নয়, কিন্তু "no recognition at all" সঠিক দাবিটি দিয়েছে |
| diag | নির্ণয় — মেরামতের ভিত্তি; ১৪৩টি লুকানো miss আর ৪টি নিয়মতান্ত্রিক mechanism নাম দেওয়া নতুন চিন্তা |
| frag | **মেরামত** (সৎভাবে বলা হয়েছে) — area floor-এর ১px ফাঁক ধরা, কিন্তু mechanism নতুন নয় |
| p01 | নেতিবাচক ফল — ভুল premise ধরা পড়েছে; "N of Nothing's" প্রমাণটি মাপার শৃঙ্খলার উদাহরণ |
| v3gate | নেতিবাচক ফল — threshold-এর সীমা মাপা হয়েছে; over-split-এর সতর্কতা মূল্যবান |
| gateside G2 | **নীতিগত, প্রায়-উদ্ভাবন** — core-কে তার শব্দের বদলে তার লাইনের কাছে বিচার করা; majority-নিয়মে কোনো নতুন magic number নেই |
| top2b | নেতিবাচক ফল — কিন্তু "wrong-cut floor" প্রমাণটি গভীর: shape একা পারে না, অর্থ লাগে |
| dbnet | যাচাই নিজে **মেরামত-যাচাই**, কিন্তু ফলটি উদ্ভাবনের দিকে আঙুল তোলে: বাধা detector নয়, prompt-নিয়ম — আর সেখান থেকে "একক-CC সাক্ষী" নতুন ভূমিকা |
| p21 reclaim2c | **R19 composition-এর নীতিগত, মাপা-যাওয়া রূপ** — gate-র নিজের threshold দিয়ে মেরামত (140-sub), "validation বিচার করে, reclaim মেরামত করে", "fragment ভোট দিতে পারে না" — LSE-র মতো নতুন প্রযুক্তি নয়, কিন্তু patch-এর বেশি |
| **merge** | composition-ই এখানে আবিষ্কারের মতো: top2a-first → validated split-এ dark-core reclaim → DP শুধু শেষ ভরসা → G2 line-band gate — প্রতিটি অংশ মাপা, আর যাচাইয়ে ধরা দুটি ভুল (stale fix, missing DP) শুধরে নেওয়া হয়েছে |

R19-র top2b (rhythm-DP) ছিল এই প্রজেক্টের উদ্ভাবন; Round 20-তে তার সমতুল্য নতুন কিছু আসেনি —
এই রাউন্ডের আসল অগ্রগতি **নির্ণয়ের গভীরতা** (dark-core/halo ফাঁক, prompt-নিয়ম বনাম detector,
wrong-cut floor) আর **যাচাইয়ের শৃঙ্খলা** (gate-অন্ধ collapse ধরা পড়েছে)। সেটা সৎভাবে বলা হচ্ছে।

---

## ১৩. Novelty / prior-art অবস্থা

- **পূর্ণ LSE সংমিশ্রণে এখনো NO HIT** (অনলাইন ট্র্যাক, §২) — কোনো shipping প্রোডাক্ট, স্টার্টআপ,
  ওপেন-সোর্স প্রজেক্ট, বা in-force পেটেন্ট নেই।
- **আইনজীবীর কাছে যাওয়া ডকুমেন্ট (কোনো verdict নয়):** Adobe US9741142B2 (OCR-ভিত্তিক, LSE-কে
  cover করে না); Xerox US5548700A (OCR-free core-র সবচেয়ে কাছের, expired 2013); **নতুন LEAD
  US 5,734,761 (Xerox, 1998)** — R19 থেকে, claims অ-পড়া; **নতুন LEAD US 20250111688 ও
  US 20250078557** (দুটোই patent APPLICATION, claims অ-পড়া) — R20 অনলাইন ট্র্যাক থেকে।
- **সৎ novelty দাবি:** "new combination and product" — আগের মতোই। আর দাবির ভাষা (§২): "no
  recognition at all — neither OCR nor VLM; geometry only"।
- IntelliDoc (OCR-ভিত্তিক) — NOT a hit। Scanned.To (VLM cloud converter) — conversion, preservation নয়।

---

## ১৪. খোলা কাজ — পরের রাউন্ডের জন্য

1. **বাকি ২টি ফ্ল্যাগ:** p01 T1 0.542 (MATA "A" core), p12 T1 0.970 — দুটিই R19-র পুরনো। p01-র
   T1a-র আসল কারণ row-split 1px limit (track-p01-র handoff); T1b "SCHEDULE" dark-threshold
   নির্ণয় আছে। p12-র কারণ আলাদা করে দেখা হয়নি।
2. **p21-র ৩টি একক অক্ষর** এখনো missing ("i", "l", "ability"-র "l") — bridged/light-letter কেস;
   এর জন্য আরেকটি reclaim নিয়ম (দুই বাক্স ছোঁয়া sub-কে ভাগ করা) লাগবে।
3. **gap-aware DP** (track-p21-র প্রস্তাব): DP-র cost-এ word-gap-এর ওজন — p21-র 42/42 আর
   canonical identity দুটোই পাওয়ার একমাত্র পথ।
4. **Detector-কে "একক-CC সাক্ষী" হিসেবে** (track-dbnet §৮ প্রস্তাব): n_cc=1 টুকরো + detector-লাইন
   মিলে prompt; বা সরাসরি লাইন-oracle (16/16)। Gate-ট্র্যাক যাচাই করে ঠিক করবে — detector কখনো
   auto-add বা auto-merge করবে না, শুধু cross-check/oracle।
5. **Gate-কে whole-line collapse ধরার চোখ দিতে হবে** (§১১.b) — একটি বাক্সে গোটা লাইন থাকলে gate
   এখন অন্ধ। সম্ভাব্য চেক: line-band-এর ভেতরে word-box-এর সংখ্যা বনাম detector-লাইন, বা
   অস্বাভাবিক চওড়া (৩০× med_h-র বেশি) একক শব্দের flag। ৩০× guard-এর ধারণাটি মাপা আছে (R19-এ
   বৈধ সর্বোচ্চ 27.0×, collapsed 52.6×) কিন্তু এই merge-এ ঢোকানো হয়নি — আলাদাভাবে যাচাই করতে হবে।
6. **frag gap-attach-কে segmenter-এ integrate করা** — p2-র ২টি rescue ("CY", "BH") score-neutral
   হলেও আসল ink coverage বাড়ায়; integration-এর পর ৩৩ পাতা আবার যাচাই করতে হবে।
7. **rav-p2-র ৫টি নতুন miss GT-তে যোগ করা** (সিদ্ধান্ত gate-ট্র্যাকের) — "CY", "17.", "o", "BH", "ou"।
8. **G2-র near-miss:** combined রানে p10-এ 1px-touch false T1 (v4-র সঙ্গে) — G2 একা p10-কে ছোঁয়নি,
   কিন্তু 1px margin নজরে রাখতে হবে। **`_row_split_blob`-এ একই আকৃতির ঝুঁকি** (orphan গোনা হয়
   `len(words) < 2` চেকে) — অমাপা, ভবিষ্যতে যাচাই দরকার।
9. **LSE এক পাতা, print calibration, US patent check, Windows .exe** — আগের মতোই খোলা (শেষ দুটি
   শুধু ব্যবহারকারীই করতে পারেন)। **Q-03–Q-09, ★2–★8, caps, gate promotion, −2 band, ১৮টি
   borderless edge** — ব্যবহারকারীর সিদ্ধান্তের অপেক্ষায় (এই রাউন্ড কিছুই settle করেনি)।
10. **Repo:** Round 20 merge (segmenter + gate + segs) public repo-তে push করার সিদ্ধান্ত parent-এর।

---

## ১৫. ফাইল তালিকা ও যাচাই (verification summary)

**এই রিপোর্ট:** `improve/ROUND20-REPORT.md`

**নতুন baseline (`improve/round20/merge-r20/`):** `segment_merged.py` (R19 fixes + reclaim2c),
`gate_merged.py` (R19 gate + G2), `logo_detect.py`, `rhythm_dp.py` (দুটোই R19-র সঙ্গে
byte-identical যাচাই করা), `segs/` (৩৩ পাতা), `gate_batch_r20_merged.json` (২৫ পাতা + p2/p3/PG),
`canon_r20_merged.json`, `run_gate_r20.py`, `apply_frag_attach.py`, `segs-frag/`,
`frag_on_merge_summary.json`। Audit trail: `segs-prefixed/`, `segs-nodp/`, `segs-frag-prefixed/`,
`gate_batch_r20_prefixed.json`, `gate_batch_r20_nodp.json`, `canon_r20_prefixed.json`,
`canon_r20_nodp.json`, `frag_on_merge_prefixed_summary.json`।

**ট্র্যাক ডিরেক্টরি:** `track-online/RESEARCH20.md` · `track-diag/DIAGNOSIS20.md` ·
`track-frag/TRACK-REPORT.md` · `track-p01/TRACK-REPORT.md` · `track-v3gate/TRACK-REPORT.md` ·
`track-gateside/TRACK-REPORT.md` · `track-top2b/TRACK-REPORT.md` · `track-p21/TRACK-REPORT.md` ·
`track-dbnet/TRACK-REPORT.md` (৩৩০ লাইন)।

**কো-অর্ডিনেটরের নিজের যাচাই (সব ✅):** merge gate নিজে চালানো (23/2); canonical scorer নিজে
চালানো (N5 40/81, Desc 39/69, redbox 7/66, p3 248/285); p21 GT scorer নিজে চালানো (35/42);
LINES rescorer নিজে চালানো (327/327); guard FULL নিজে চালানো (5/5 PASS); frag/gateside/dbnet
gate+eval JSON সরাসরি পড়ে মোট মিলিয়েছি; R19 segmenter নিজে চালিয়ে may-p2/may-p3 (313/306)
আর p21 GT (33/42) মেপেছি; Round 3 DB SHA `1c065457bb9c…` কাজের আগে ও শেষে একই (DB শুধু পড়া
হয়েছে, লেখা হয়নি)। কোনো আগের রাউন্ডের রিপোর্ট, DECISIONS-PENDING.md বা prototype original ছোঁয়া
হয়নি। সব লেখা শুধু `round20/`-তে। Drive-এ আপলোড হয়নি, MEMORY.md ছোঁয়া হয়নি (নির্দেশ অনুযায়ী)।

**শেষ কথা:** Gate 17/8 → 23/2 — Round 20-র সংখ্যা ভালো। কিন্তু এই রাউন্ডের আসল ফল সংখ্যার চেয়ে
বড়: নির্ণয় এখন জানে বাধা কোথায় (dark-core/halo ফাঁক, prompt-নিয়ম, shape-এর floor), আর যাচাই
এখন জানে gate কী দেখে না (whole-line collapse)। বাকি ২টি ফ্ল্যাগ আর ৩টি একক অক্ষর — সেটাই
পরের রাউন্ডের আসল পুরস্কার।
