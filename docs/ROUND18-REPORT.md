# ROUND 18 — রিপোর্ট (LSE Live-Scan Editing)

**তারিখ:** ২০২৬-১১-০৭ • **মার্জ ডিরেক্টরি:** `improve/round18/merge-r18/` • **ট্র্যাক:** A (V1 page-Otsu-clip, universality), B (DBNet header-zone UI + DPI + gate, ২৫টি Raviraj পাতা), C (caps ব্রিফ + idx307 seam + bold + Q-03–Q-09)

## এক লাইনে

**কোনো স্কোর বদলায়নি। ৫টি লাইভ পাতা byte-identical (এবার Aug-এর ১-অক্ষরের diagnostic পার্থক্যটাও নেই — R16-র মতো ৫/৫)। DB অক্ষত (SHA `1c065457…`, ২০টি audit entry, LSE-0001–0007)।** তিন ট্র্যাকেরই কাজ প্রমাণসহ শেষ: V1 **পরীক্ষামূলকই থাকল — PROMOTE নয়** (Tottel-এ হারে, PG-তে BY|SALES জোড়া লাগায়); gate ২৫টি নতুন Raviraj পাতায় **৯ ALLOW / ১৬ REFUSE** (seg-ই ঘাটতি, gate ঠিক আছে); bold **আনুষ্ঠানিকভাবে গ্রহণ** — Lot-anchor + heading flip-ই ডিজাইন; caps, seam, Q-03–Q-09 — সিদ্ধান্ত-ব্রিফ তৈরি, কোনোটিই সিদ্ধান্ত নেওয়া হয়নি।

## §1. মার্জ যাচাই — নিজের পুনঃচালনার সংখ্যা (সবুজ = R17-র সঙ্গে অভিন্ন)

| পরীক্ষা | ফলাফল (R18 মার্জের নিজের চালনা) | R17 |
|---|---|---|
| লাইভ পাতা rebuild (r18m builders) | **৫/৫ byte-identical** — Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2 `539995a9…`, May p3 `8587be86…` | ৫/৫ (Aug-এ ১-অক্ষর diagnostic পার্থক্য ছিল) |
| segs (r17m → r18m) | `diff -r` খালি — **অভিন্ন** | অভিন্ন |
| heading JSON (৫টি) | r17m-র সঙ্গে **৫/৫ অভিন্ন** (R11-র সঙ্গে যাচাইকৃত) | ৫/৫ |
| fontfix_verify300 | **৪৩/৪৩** | ৪৩/৪৩ |
| verify_round2_300 ×২ | **১৮/১৮ ×২**, দুই চালনার পরও SHA+mtime অপরিবর্তিত | ১৮/১৮ ×২ |
| LINES rescore (r18m scorer) | **৩২৭/৩২৭ CONFIRMED** | ৩২৭/৩২৭ |
| p3 score | strict **৩৩৪/৩৮৪**, improved **৩৮৪/৩৮৪ = ১০০%** | একই |
| p2 strict / corrected / improved | ৪৪৭/৫০২ = ৮৯.০% / ৪৯৮/৫০২ = ৯৯.২% / ৪৫১/৫০২ | একই |
| পূর্ণ পাতা (৮৮৬) strict / corrected / improved | ৭৮১/৮৮৬ = ৮৮.১% / ৮৩২/৮৮৬ = ৯৩.৯% / ৮৩৫/৮৮৬ = ৯৪.২% | একই |
| N5 | strict **৭৭/৮১**, improved **৮১/৮১** | একই |
| Description | **৬৯/৬৯** (r10 GT-তে; stale r9 GT-তে ৬৩/৬৯ — r9 GT stale, r10-ই canonical) | ৬৯/৬৯ |
| redbox | r12 **৬৬/৬৬**; R9 canonical **১৫/৬৬** | একই |
| PG sample | **৫১৮/৫১৮**, extras ০ | একই |
| Guard check (full mode, ৫ পাতা) | **৫/৫ PASS** (C1–C5 সব, exit 0) | ৫/৫ |
| Identity probe (FIXED r14m probe, r18m copy) | **১৫/১৫ PASS ×৩ চালনা**; ক্লিপ চোখে যাচাই (Aug p2 WIDTH-তে 776.5, Hard অক্ষত; Aug p1 Lot-এ 207/9) | ১৫/১৫ |
| Universality scorer (অথরিটেটিভ) | **byte-identical** — stored `scorer_out.txt`-এর সঙ্গে হুবহু | byte-identical |
| repro300 | **PASS** — ২টি edited span, exact text, .done, no doubling | PASS |
| manual_proof300 | **১০/১০** | ১০/১০ |
| Write-back (300 verifier) | **৩৭/৪১** — ৪টি FAIL শুধু ink IoU (মান R17-র সঙ্গে হুবহু: 0.311 / 0.407 / 0.339 / 0.411 — stand-in ফন্টের জানা সীমা, regression নয়) | ৩৭/৪১ |
| Write-back (r10 verifier) | **৪১/৪১, FAILURES: none** | ৪১/৪১ |
| Track D staging | **৪৮/৪৮** | ৪৮/৪৮ |
| Track C staging | **৭৪/৭৪** | ৭৪/৭৪ |
| May multipage | **৫৯/৫৯** | ৫৯/৫৯ |
| May p2/p3 verifier | **৪৩/৪৩** | ৪৩/৪৩ |
| sqlcipher | **১৫/১৫** | ১৫/১৫ |
| keymgmt | **২৫/২৫** | ২৫/২৫ |
| save→label (live verifier r10b) | **৯০/৯০** (৫ পাতা × ১৮/১৮) | ৯০/৯০ |
| Aug p2 verifier | **১৬/১৬** | ১৬/১৬ |
| Heading R1 | **PASS 14/14 ×৩ family** (TITLE 14/14, H2 14/14, H1-diff ২) | একই |
| Shared DB (read-only) | SHA `1c065457bb9cb8e5…`, **৭টি delivery (LSE-0001–0007), ২০টি audit entry, chain linked ২০/২০** | একই |

**মার্জ-প্রক্রিয়ার নোট (R17-র ভুল আর হয়নি):** probe-র MG এবার শুরুতেই যাচাই করা হয়েছে — `probe_identity_r18m.py`-তে MG = `round18/merge-r18`, stale রেফারেন্স ০টি; probe JSON + ক্লিপ merge-r18-তেই লেখা হয়েছে (r17m অক্ষত)। সেড-রিডাইরেক্টের ভুল এড়াতে কপি Python দিয়ে করা হয়েছে, input ফাইলের ওপর কখনো redirect নয়।

**একটি নতুন পর্যবেক্ষণ — ক্লিপ SHA ওঠানামা (পাতা/seg-এর পরিবর্তন নয়):** একই probe তিনবার চালালে Aug p2 WIDTH ক্লিপের SHA দুইবার `9d7d76de…` (R15–R17-র সঙ্গে অভিন্ন) আর একবার `289ae8c5…` এসেছে — চোখে দেখা বিষয়বস্তু ও byte size (২৫,৩৭১) তিনবারই হুবহু এক, probe তিনবারই ১৫/১৫ PASS। এটা Playwright স্ক্রিনশট-রেন্ডারিংয়ের nondeterminism (sub-pixel antialiasing-এর ওঠানামা), পাতা বা seg বদলায়নি — পাতার SHA অপরিবর্তিতই প্রমাণ। ক্লিপ SHA-কে তাই আর "পাতা অপরিবর্তিত"-র প্রমাণ হিসেবে ব্যবহার করা যাবে না; probe-র PASS-ই মানদণ্ড।

**save→label সংশোধন:** প্রথম চালনায় পুরনো `verify_save_label.py` (ডিফল্ট ২ পাতা, ১৭ চেক/পাতা) চালানো হয়েছিল — সেটা ভুল স্ক্রিপ্ট। সঠিকটি `verify_save_label_live_r10b.py` (৫ পাতা × ১৮/১৮ = **৯০/৯০**) — R17-র লগের ফরম্যাটের সঙ্গে মিলিয়ে যাচাই করা হয়েছে। পুরনো স্ক্রিপ্টের EXPECT-এ may-p1/may-p3 নেই (KeyError হয়) — ওটা আর ব্যবহার করা যাবে না।

## §2. Track A — V1 page-Otsu-clip, universality sample (EXPERIMENTAL, PROMOTE নয়)

**কাজ:** R17-র একমাত্র বেঁচে-থাকা adaptive প্রার্থী V1-কে অথরিটেটিভ scorer দিয়ে FUNSD/SROIE/Tottel/Shields-এ (base + valley) মাপা; hybrid (V1 + SALES-line guard-এর analogue) দিয়ে BY|SALES ব্যর্থতা সারানো যায় কি না দেখা।

**মার্জের নিজের যাচাই:** scorer পুনঃচালনা stored `scorer_out.txt`-এর সঙ্গে byte-identical (calibration PASS — ৭টি ডকেই পুরনো সংখ্যা হুবহু ফেরে: base ৫১/১০৩, valley ৫৮/১০৩)। `score_variants_out.txt` থেকে মোট:

| স্যাম্পল | fixed 0.25 | V1 | hybrid |
|---|---|---|---|
| base (১০৩) | ৫০ | **৬৬** | ৫০ |
| valley (১০৩) | ৪৭ | **৬২** | ৪৭ |

প্রতি ডক (base): FUNSD fixed ২১ → **V1 ৩২ (+১২/−০)**; SROIE ২ → **১১ (+৮/−০)**; Tottel ১৮ → **১৪ (হারে)**; Shields ৯ → ৯ (পুরনো seg-এর ১২-র চেয়ে খারাপ)। Valley: FUNSD ১৮ → ২৯, SROIE ২ → ১০, Tottel ১৪, Shields ৯।

**PG BY|SALES (পুনঃমাপা):** V1 জোড়া লাগায় **১২/১৪** পাতায়; hybrid ৮/১৪, fixed ৮/১৪। ১৬ পাতায় মোট error: V1 **৭৮**, hybrid ১৩১, fixed ১৩১ — hybrid ঠিক fixed-এর সমান (guard লাভটাই মুছে দেয়)।

**চোখে যাচাই (মার্জ):** Tottel LV2 false-merge ক্রপ — V1-র সবুজ বাক্স "Henry Haward"-কে **একটি** বাক্স করেছে (৪টি শব্দ এক বাক্সে)। এটাই নির্ণায়ক প্রমাণ।

**রায়: EXPERIMENTAL, DO NOT PROMOTE।** V1-র লাভ আর ক্ষতি একই mechanism — নির্বিচার জোড়া-লাগানো। চাপা ছোট ছাপায় (FUNSD/SROIE) ভাঙা টুকরো জোড়া লাগিয়ে সত্যিকারের শব্দ ফিরিয়ে আনে; ফাঁকা-ফাঁকা বড় ছাপায় (Tottel) আর PG-র SALES লাইনে আলাদা শব্দ জোড়া লাগিয়ে দেয়। একটিমাত্র পাতা-threshold দুই ধরনের কাগজে একসঙ্গে ঠিক হতে পারে না — Otsu threshold universality-তে ০.৩৪–০.৫০ (PG-তে ছিল ০.২৪৬–০.৩৩৩), doc বদলালে threshold-ই অস্থির। Promotion-এর bar পার হয়নি: (ক) কোনো doc-ধরনে হার চলবে না — Tottel-এ হেরেছে; (খ) BY|SALES জোড়া লাগানো চলবে না — ১২/১৪; (গ) guard-কে লাভ রেখে ক্ষতি থামাতে হবে — hybrid লাভটাই মুছে দেয়। **Adaptive word-gap এই রাউন্ডে শেষ — আর কোনো প্রার্থী বাকি নেই।**

## §3. Track B — DBNet header-zone UI প্রস্তাব + DPI-scaling + gate, ২৫টি Raviraj পাতা

### ৩.১ UI প্রস্তাব (সিদ্ধান্ত নয় — প্রোডাক্ট-সিদ্ধান্তের প্রস্তুতি)

- **মূল জায়গা template capture-সময়; delivery-সময় কোনো prompt নয়।**
- Confirm = মানুষ crop দেখে শব্দটি টাইপ করে (Signal B) বা verification mark দেয় (Signal A); dismiss = exclusion list-এ যায়।
- **কখনো auto-add / auto-merge নয়; prompt-এ OCR-পাঠানো text নয় — শুধু crop + প্রমাণ-সংখ্যা।**
- R17-র সংখ্যা নিজে পুনঃচালনায় যাচাই: Signal B **২৮/২৮ real, ০ false alarm**; Signal A real শব্দে ০ false flag, **৩টি non-word prompt / ১৬ পাতা**।

### ৩.২ DPI-scaling — পরীক্ষায় সঠিক

`zone(DPI) = 285 × DPI/300 px` (০.৯৫ ইঞ্চি × DPI)। aug-p1-এ ৩০০/২০০/১৫০ DPI-তে: Signal B **২/২** (PREM+GROUP), DBNet লাইন **১২৬** তিন DPI-তেই, বাক্সের স্থানাঙ্ক scaling-এর সঙ্গে হুবহু মেলে। (সীমা: এটা zone-নিয়মের পরীক্ষা — ২০০ DPI-তে seg নতুন করে করা হয়নি, geometrically scaled।)

### ৩.৩ Raviraj zone — একটিমাত্র ২৮৫px সব ফর্মে চলে না

২৫ পাতায় zone ২৮৫ বনাম ৪০০: Signal B **২০ → ৪০**, Signal A **৪৯ → ৬৩**। ৪০০px আসল miss ধরে (p04 "BENEFICIARY" লেবেল y৩৮৬–৪০৪, p13–p15 consignee লাইন)। **প্রস্তাব: Raviraj ফর্মে ৪০০px, PG-তে ২৮৫px; COA দুটোতেই একই। Zone ফর্মের নিজের header extent থেকে আসা উচিত, হাতে-লেখা সংখ্যা থেকে নয়।** (সিদ্ধান্ত নয়।)

### ৩.৪ Gate — ২৫টি অন্যান্য Raviraj পাতা (মার্জের নিজের পুনঃচালনায় যাচাই)

**৯ ALLOW / ১৬ REFUSE** — Track B-র দাবির সঙ্গে হুবহু মেলে (ALLOW: p04, p05, p06, p07, p20, p23, p24, p25, p26; REFUSE: p01, p08–p19, p21, p22, p27)। REFUSE-গুলো আসল seg-miss (হালকা নীল কালি, সবুজের ওপর নীল লেখা, স্ট্যাম্প-ঢাকা শব্দ, ছোট ঘন ছাপা) — gate seg-এর ঘাটতিই মাপছে, gate নিজে ভুল করছে না। প্রমাণ: p2/p3 canonical ALLOW, একই পাতার fresh v5 seg REFUSE।

**T1 threshold ০.৫০ দাঁড়িয়ে আছে:** সর্বোচ্চ সঠিক কল ০.৪৮৪ (rav-p2, R17-র মান পুনঃমাপায় হুবহু); আমার ব্যাচে সর্বোচ্চ ALLOW ০.৪৭৭; সর্বনিম্ন flag ০.৫০৯ (ভাঙা "ORIGIN", চোখে যাচাইকৃত)। ব্যবধান মাত্র ০.০২৫, কিন্তু গুণগতভাবে আলাদা (আঁটসাঁট বাক্স বনাম ভাঙা/মিস করা অক্ষর)।

**Controls (আমার পুনঃচালনা):** rotated JPG REFUSE **T1=138 T2=253** (R17-র সঙ্গে হুবহু); rotated-back ALLOW; synthetic miss (p07/p23 আসল শব্দ) REFUSE — ঠিক বাক্সসহ। একটি synth-miss (৯×৩ px speck) ALLOW হয়েছে — সেটা সঠিক, control-নির্বাচনের ভুল (speck শব্দ নয়)।

**-2 (ambiguous) core — প্রস্তাব:** band-আকৃতির -2 core (cw>120) mask থেকে বাদ দেওয়া হোক, বাকিটা থাকুক। May-র dotted band ৪৪৯px চওড়া, ~১৪.৫k mask px/পাতা — এটা টাইটেলের ধূসর highlight, শব্দ নয়; fused-letter -2 core সর্বোচ্চ ৭৮px; band সর্বনিম্ন ৩০৭px — ১২০ সংখ্যাটি ৭৮→৩০৭ ব্যবধানের ভেতরে পরিষ্কারভাবে বসে। **চোখে যাচাই (মার্জ):** T2 ক্রপে "CITY" — আসল হালকা-নীল কালির শব্দ, seg মিস করেছে (সত্যিকারের flag); -2 band ক্রপে "-2 area=12868" — "ANALYTICAL TEST REPORT" টাইটেলের পেছনের dotted highlight band, শব্দ নয় (প্রস্তাব সঠিক)।

**Orientation:** ২৫/২৫ পাতা চোখে সোজা (contact sheet); p05 R4-র ১৮০° সংশোধন প্রয়োগ করা হয়নি (R4-র একমাত্র miss); flip3 ৬ পাতায় ভুল — চোখে দেখাই চূড়ান্ত প্রমাণ।

**সীমা (Track B-র নিজের স্বীকারোক্তি):** T1 margin পাতলা (০.০২৫); gate-ফল raw v5 seg-এর ওপর; Signal B-র সব flag আলাদা করে চোখে দেখা হয়নি (নমুনা ৪+১); DBNet timing ব্যবহারকারীর i5-এ মাপা হয়নি।

## §4. Track C — caps ব্রিফ + idx307 seam + bold (acceptance) + Q-03–Q-09

### ৪.১ Caps — সিদ্ধান্ত-ব্রিফ (প্রস্তাব, সিদ্ধান্ত নয়)

৬৪px স্লটে কোনো ফন্টই ফিট করে না — নিজে পুনঃমেপে নিশ্চিত: DejaVu Bold ১২২px (+৫৮), সংকীর্ণতম **Noto Sans ExtraCondensed Bold ৮৬px (+২২)**, ফিট করে শুধু **৯২px স্লটে**। Squeeze ×০.৫২৫/×০.৭৪৪; shrink-to-fit-এ cap height ৩৭ → ১৯.৪px (cap-height মিল ভেঙে যায়)। Document DNA অনুমান নিজে মেপে যাচাই: DHAKA idx312 কালি ৭৯×২০px (৫ অক্ষর), BANGLADESH idx316 ১৬৩×২০px (১০ অক্ষর) → ৩৭px cap-height-এ AND = **৮৭.৭/৯০.৫px** (সৎ পরিসর ~৮৭–৯১px, period-সতর্কতাসহ)।

- **বিকল্প A:** ExtraCondensed + ৯২px স্লট + ব্যবহারকারীর নিশ্চিতকরণ (দুই পাশে ৩/৩px ফাঁক; caps বড় দেখাবে)।
- **বিকল্প B:** lowercase সাজেশন।
- সিদ্ধান্ত না হলে ডিফল্ট: caps শুধু যেখানে ফিট করে, নইলে lowercase সাজেশন।

### ৪.২ idx307 seam-lightening — pixel-স্তরে নিরাপদ, কিন্তু দৃশ্যমান লাভ নেই

নিজে পুনঃচালনায় যাচাই: V150/V180/V210 তিনটিতেই **core_rem ১০০.০% (০px অবশিষ্ট), R_other ১০০.০% অক্ষত**; বদলানো pixel ঠিক **১৪টি**, residual সেটের সঙ্গে অভিন্ন, বাইরে ০টি; zone ৩১২/৩১৪ diff ০, zone ৩১৩ −১৪px = residual নিজেই। Regression idx308/309/310/311 সব **১০০%/১০০%**; and→or পথ অপরিবর্তিত (shared module sha256 `e9556f78…5631`, অছোঁয়া)।

**চোখে যাচাই (মার্জ, ৮× ক্রপ):** V150 আগের মতোই; **V210 "M"/"A"-র মাথায় সাদা notch বানায়**; ১×-এ দুটোই অদৃশ্য। **রায়: ২১০ নয়; ১৫০ শুধু metric-এর জন্য ঐচ্ছিক (১৩৩→১৫০ threshold-পার, আসল অপসারণ নয়); ডিফল্ট যেমন আছে তেমনই থাকুক।**

**সংশোধন:** R17-র "০.০px দূরে" দাবিটি coarse সেটের বিরুদ্ধে ছিল — R_other-এর বিরুদ্ধে দূরত্ব **২.৯px**।

### ৪.৩ Bold — নতুন signal-ও ব্যর্থ, ACCEPTANCE

RULEMASK-STROKE (প্রথমে পাতা-স্তরে rule mask, তারপর median-DT stroke thickness — run-length বা DT-mean-এর পুনরাবৃত্তি নয়) — নিজে পুনঃচালনায় যাচাই: **১৪/২৯ = ৪৮.৩%, FP ১৭, ০/৬ পাতায় আলাদা হয়**; control unmasked ১৪/২৯, FP ২১। Masking দূষণ সারিয়েছে (প্রমাণ: aug-p2 লাইন ২০/২২ — ১২.৫৩×/৪.৪৭× → ১.০৩৭×/০.৮৯৭×; ১৭৯টি word box-এ ৫৬,৪১৫টি rule-pixel; overlay ক্রপে লাল শুধু grid-এ, glyph-এ নয়) — কিন্তু May-র bold ≈ anchor (১.০০–১.০৪ বনাম regular ১.০৬–১.০৮)। তিনটি স্বতন্ত্র মাপ-পরিবার একই কাঠামোগত কারণে ব্যর্থ।

**ACCEPTANCE: Lot-anchor (PG-only, 0.036 HOLD) + heading flip-ই ডিজাইন; নতুন টেমপ্লেটে automatic bold detection থাকবে না** — bold টেমপ্লেটে চিহ্নিত থাকবে, অথবা known-regular-word anchor দিয়ে।

### ৪.৪ Q-03–Q-09 + ১৮টি borderless edge — সিদ্ধান্ত-ব্রিফ (এক লাইনে প্রতিটি; কোনোটিই সিদ্ধান্ত নয়)

| প্রশ্ন | প্রস্তাব | সিদ্ধান্ত না হলে (ইন্টিগ্রেশন ডিফল্ট) |
|---|---|---|
| Q-03 — সাপ্লায়ার COA-তে LSE-র গ্রহণযোগ্য মান কত? (Raviraj এখন strict ৮৮.১% / lenient ৯৩.৯%) | **৯০%+** (ডিজাইন ডকের ৭৪.৩% পুরনো — চিহ্নিত) | শুধু PG-মানের পাতায় LSE, বাকিটায় হাতে-যাচাই মোড; Raviraj-ধরনের পাতা প্রোডাকশন-LSE পাবে না |
| Q-04 — US পেটেন্ট US20150332491A1 উকিলের যাচাই কখন? | Phase 1 শেষ হওয়ার আগেই | যাচাই ছাড়া বিক্রি নয় — বিল্ড চলবে, বিক্রির সময়সূচি আটকাবে |
| Q-05 — ফ্যাক্টরির প্রিন্টার মডেল? | মডেলের নাম দিলেই ক্যালিব্রেশন-ফাইল বানানো যাবে | প্রিন্ট ক্যালিব্রেশন শুরুই হবে না (শুধু তাঁর হাতে করা যায়) |
| Q-06 — Vault-এর canonical পাথ? | দ্বিতীয়টি (বছরসহ, COA_Label-সহ) | দ্বিতীয় পাথ (পরিবর্তনযোগ্য) |
| Q-07 — বুদ্ধিমত্তা: সতর্কতা নাকি শুধু সম্পর্ক? | সতর্কতা + সম্পর্ক — কিন্তু সতর্কতা কখনো ব্লক নয় | সতর্কতা দেখানো হবে, কখনো ব্লক নয় |
| Q-08 — স্ক্যান COA টেমপ্লেট হিসেবেও intake হবে? | দুটোই — intake-এ ব্যবহারকারী বেছে নেবে | intake-এ বেছে নেওয়ার বিকল্প থাকবে |
| Q-09 — ১৮টি borderless edge? | **হুবহু রাখা** (faithful-ই প্রতিশ্রুতি) | হুবহু রাখা — বর্ডার যোগ করা হবে না |

Q-01/Q-02 এই ট্র্যাকের scope-এ নেই (ব্যবহারকারীর ২০২৬-১১-০৭ ~২২:২৯ পুনর্ব্যক্তি — LSE GRAVORA-তে MODULE হিসেবে + আলাদাভাবে GitHub-এ — এখনো স্পষ্টীকরণের অপেক্ষায়; ইন্টিগ্রেশন বিল্ড তার উত্তরের অপেক্ষায়)।

## §5. সৎ সীমা — যা এখনো খোলা

- **প্রিন্ট ক্যালিব্রেশন** (ফ্যাক্টরির প্রিন্টার — শুধু ব্যবহারকারী পারেন), **US পেটেন্টের উকিল-যাচাই** (Adobe US9741142B2 প্রথমে) — দুটোই তাঁর হাতে, permission-এর বিষয় নয়।
- **DBNet swap deferred** (KEEP CLASSICAL সিদ্ধান্ত); DBNet header-zone signal শুধু review prompt হিসেবে (প্রস্তাব)।
- **DPAPI** VM-এ অপ্রমাণিত; `raviraj COA 20 micron.jpg` পাওয়া যায়নি; ১৮টি borderless edge ব্যবহারকারীর সিদ্ধান্তের অপেক্ষায় (Q-09)।
- **T1 margin পাতলা** (০.০২৫) — gate build-time promotion প্রোডাক্ট-সিদ্ধান্ত, নেওয়া হয়নি।
- **Caps নীতি** সিদ্ধান্ত হয়নি (ব্রিফ তৈরি); **seam-lightening** ডিফল্ট যেমন আছে তেমনই; **bold** acceptance হিসেবে বন্ধ।
- **Adaptive word-gap শেষ** — V1-ই ছিল শেষ প্রার্থী, আর কোনো প্রার্থী বাকি নেই। Universality-তে segmentation এখনো দুর্বল (FUNSD base ২০/৩৮, SROIE ৪/১৬, Tottel ১৬/২৪, Shields ১২/২৫ — মোট ৯৪/১৮২)।
- **redbox L5 'and'** এখনো counted miss — কালি শারীরিকভাবে নেই (০ px), বানানো হবে fabrication।
- **p3 strict-এর ৫০টি miss সবই artefact** (আসল ০) — improved-ই p3-র সৎ মাপ; median কখনো টানা যাবে না।
- **Q-03–Q-09** কোনোটিই সিদ্ধান্ত নয় — ইন্টিগ্রেশন reversible ডিফল্টে চলবে।
- **Q-01 স্পষ্টীকরণ বাকি** — LSE module বনাম engine (ব্যবহারকারীর পুনর্ব্যক্তি বনাম ডিজাইন ডক)।

## §6. Round 19-র প্রস্তাব + ইন্টিগ্রেশন প্রস্তুতি

**LSE core ৩ রাউন্ড ধরে স্থিতিশীল** (R16–R18 কোনো স্কোর বদলায়নি, পাতা ৫/৫ byte-identical, DB অক্ষত) — ইন্টিগ্রেশন বিল্ডের জন্য প্রস্তুত। Round 19-র প্রার্থী (ক্রমানুসারে):

1. **Gate T1 margin বাড়ানো** — ২৫ পাতার REFUSE-গুলোর seg-ঘাটতি (হালকা নীল কালি, স্ট্যাম্প-ঢাকা শব্দ) সারানো গেলে ALLOW বাড়বে; T1-র ০.০২৫ ব্যবধান তখন আরো নিরাপদ হবে।
2. **-2 band-নিয়ম (cw>120) প্রোডাক্ট-সিদ্ধান্তে তোলা** — May-র টাইটেল-band প্রমাণসহ; build-time promotion-এর সঙ্গে একসঙ্গে সিদ্ধান্ত নেওয়া যায়।
3. **Caps সিদ্ধান্ত** (বিকল্প A বনাম B) — ব্যবহারকারীর এক লাইনের উত্তরেই হবে।
4. **Header-zone signal-এর UI** — capture-time prompt-এর প্রস্তাব আছে; প্রোডাক্ট-সিদ্ধান্ত হলে ইন্টিগ্রেশনে বাঁধা যায় (DPI-scaling প্রমাণিত)।
5. **Q-03–Q-09** — ব্যবহারকারীর সিদ্ধান্তের অপেক্ষায়; কোনোটিই বিল্ড আটকায় না (reversible ডিফল্ট আছে)।

**পরের বড় ধাপ ইন্টিগ্রেশন ফেজ** (ডিজাইন তৈরি, বিল্ড চলছে) — LSE engine হিসেবে M06/M02/M18-এ বাঁধা, save→label→স্থায়ী DB রেকর্ড (৯০/৯০ যাচাইকৃত)।

## §7. ফাইল ও প্রমাণ

- এই রিপোর্ট: `improve/ROUND18-REPORT.md` (+ কপি `improve/round18/merge-r18/ROUND18-REPORT.md`)
- ট্র্যাক রিপোর্ট: `improve/round18/track-a/TRACK-A-REPORT.md`, `track-b/TRACK-B-REPORT.md`, `track-c/TRACK-C-REPORT.md`
- মার্জ ডিরেক্টরি: `improve/round18/merge-r18/` (segs, pages, clips, verify-logs — সব যাচাই-লগ এখানে)
- লাইভ পাতা: root-এ অপরিবর্তিত (SHA R11 থেকে একই); DB: `improve/round3/track-c/lse_gravora.db` (read-only যাচাই, SHA `1c065457bb9cb8e5…`)

## §8. সংশোধন (২০২৬-১১-০৮)

§৪.৪ ও §৫-এর "Q-01 স্পষ্টীকরণ বাকি" — **ভুল, এখন সিদ্ধ।** ব্যবহারকারী ২০২৬-১১-০৭ ~২২:৩১ নিজে জানিয়েছেন: LSE COA/template/supplier module-গুলোর ভেতরে editing-প্রযুক্তি হিসেবে থাকবে। ইন্টিগ্রেশন বিল্ড ওই স্থাপত্যেই চলছে।
