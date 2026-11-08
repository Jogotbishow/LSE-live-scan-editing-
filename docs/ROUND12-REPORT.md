# LSE — Round 12 রিপোর্ট

**তারিখ:** ২০২৬-১১-০৭ • **সমন্বয়কারী:** Round 12 coordinator (মূল চ্যাটে একমাত্র) • **৩ ট্র্যাক + মার্জ**

## ০. এক নজরে

| মাপ | R11 (সত্য) | **R12** |
|---|---|---|
| Raviraj p2 strict (canonical redbox scorer) | ৩৭৮/৫০২ (৭৫.৩%) | **৪১৪/৫০২ (৮২.৫%)** |
| Raviraj p2 strict (সংশোধিত redbox GT) | ৩৭৪/৫০২ | **৪৬৫/৫০২ (৯২.৬%)** |
| Raviraj p2 improved (canonical) | ৩৮২/৫০২ | **৪১৮/৫০২** |
| Raviraj p2 improved (সংশোধিত GT) | ৩৭৮/৫০২ | **৪৬৯/৫০২ (৯৩.৪%)** |
| Raviraj p3 strict (নতুন span-level GT, ৩৮৪) | ২৫০/৩৮৪ (৬৫.১%) | ২৫০/৩৮৪ (পরিবর্তন নেই — GT-ই নতুন) |
| Raviraj p3 improved | ২৯২/৩৮৪ (৭৬.০%) | ২৯২/৩৮৪ |
| **পূর্ণ পাতা strict (canonical, হর ৮৮৬)** | ৬২৮/৮৮৬ (৭০.৯%) | **৬৬৪/৮৮৬ (৭৪.৯%)** |
| **পূর্ণ পাতা strict (সংশোধিত GT, হর ৮৮৬)** | ৬২৪/৮৮৬ (৭০.৪%) | **৭১৫/৮৮৬ (৮০.৭%)** |
| **পূর্ণ পাতা improved (canonical, হর ৮৮৬)** | ৬৭৪/৮৮৬ (৭৬.১%) | **৭১০/৮৮৬ (৮০.১%)** |
| **পূর্ণ পাতা improved (সংশোধিত GT, হর ৮৮৬)** | ৬৭০/৮৮৬ (৭৫.৬%) | **৭৬১/৮৮৬ (৮৫.৯%)** |
| LINES | ২৬২/৩২৭ | **২৯৪/৩২৭** |
| Redbox (নতুন hand-verified GT) | — | **৬৬/৬৬** |
| N5 | ৭৭/৮১ strict, ৮১/৮১ improved | **অপরিবর্তিত — কোনো regression নেই** |
| Description | ৬৯/৬৯ | **অপরিবর্তিত — কোনো regression নেই** |
| False merges | — | **০** |

**R11 → R12 লাভ:** strict canonical +৩৬, strict সংশোধিত **+৯১**; improved canonical +৩৬, improved সংশোধিত **+৯১**।

**সবচেয়ে বড় সংশোধন (Track B): ৭৯৫ হরটি ভুল ছিল। Raviraj পূর্ণ পাতার সত্যিকারের শব্দসংখ্যা ৮৮৬ (p2 ৫০২ + p3 ৩৮৪), ৭৯৫ নয়।** R5-এর হাতে-গোনা ২৯৩ ছিল আঞ্চলিক নমুনা — মাঝখানের ~৯১ শব্দের ব্লক (Exporter's reference, Country, credit/IRC/TIN/BIN, pre-carriage/vessel/port/terms) তার অঞ্চলের বাইরে ছিল। R11-এর দাবি করা ৬৪৩/৭৯৫ (৮০.৯%)-এর সত্য মান ৬২৮/৮৮৬ (৭০.৯%)।

**দ্বিতীয় সংশোধন (মার্জ): Track A-র টেবিলে সংশোধিত লাভ +৮৭ লেখা ছিল — সেটি ভুল। সত্য লাভ +৯১।** Track A canonical R11 baseline ৩৭৮-কে সংশোধিত সারিতেও বসিয়েছিল; সংশোধিত R11 baseline আসলে ৩৭৪ (= ২৬২ LINES + ৭ redbox নতুন GT-তে + ১০৫ অন্যান্য)। তাই সংশোধিত লাভ ৪৬৫ − ৩৭৪ = **+৯১**, +৮৭ নয়।

## ১. Track A — Raviraj p2: E-ce ২৭ + redbox ৫৫ (সম্পূর্ণ)

**E-ce (দুই-সারি বিচ্ছেদ):** underline-rule (≥৬০px) সরিয়ে sub-band x-projection — সারি A ব্যান্ড [১৪২৭,১৪৫৪] gap≥৮, সারি B [১৪৬০,১৪৭৬] gap≥৫ (১৭টি span = ঠিক ১৭টি GT শব্দ; মূল সংশোধন: ৮px A–K gap-ই DHAKA→MAIN সীমানা), সারি C [১৪৮০,১৫০০] gap≥৬। ৭টি fused box সরানো, ২৭টি যোগ — প্রতিটি box labelled overlay-তে চোখে যাচাই করা।

**E-ce ফল:** E-ce-1 ১৩/১৩, E-ce-2 ১৭/১৭, E-ce-3 ১২/১২, E-ce-4 ৭/৭ — **মোট ২৭/২৭**। D-caution বাড়তি: দুটি ৮px-gap split (This/consignment, be/delivered) + 'Caution' তার split অর্ধেক থেকে জোড়া ('o' x২১০৩–২১৪২ uncover) — **D-caution এখন ২৭/২৭**।

**Redbox — আগের তিনটি ধারণার মাপা সংশোধন:**
1. ডান border **x১০০০–১০০৫-এ, x৮৯৮–৯০৫-এ নয়** — লাল অনুচ্ছেদ ৩৫৩–১০০৫ চওড়া; R9 scorer-এর xb=৯০০ প্রতিটি লাইনের শেষ শব্দ কেটে দিত।
2. R9 শব্দতালিকায় 'order' L8-এ, কিন্তু আসলে সেটি **L7-এর ৯ম শব্দ** (CC y১১৫০–১১৬৭) — L7-এ ৯টি শব্দ, L8-এ ৫টি।
3. R9 GT গ্রুপগুলো grey-Otsu fragment ('control' = ৪px) — কোনো আসল word box ০.৯০ দুদিকে মেলাতে পারে না; তাই canonical সংখ্যা মাত্র ১১→১৫ নড়ে, সংশোধিত GT-তে ৬৬/৬৬।

নতুন GT (`redbox_groups_r12.json`) + নতুন scorer (`scripts/redbox_score_r12.py`) — R9 scorer ছোঁয়া হয়নি। ১১৯টি grey fragment সরানো (সবগুলোই লাল কালি প্রমাণিত, mean redness ৩৯.৯–৭৩.৯ — কোনো কালো-ছাপ box সরানো হয়নি), ৬৬টি word box যোগ, সব চোখে যাচাই করা। **একটি সৎ ফ্ল্যাগ:** L5 'and'-এর শুধু 'a' বেঁচে আছে ('nd'-এর কালি নেই, max redness ≤৯, কাগজের স্তর) — গোনা হয়েছে, কিন্তু ফ্ল্যাগ করা আছে।

**p2 গাণিতিক যাচাই (সমন্বয়কারীর নিজের হিসাব):** p2 strict = LINES-সঠিক + redbox-সঠিক + অন্যান্য-outside-সঠিক (১০৫, R11 থেকে উদ্ভূত: ৩৭৮ = ২৬২ + ১১ + ১০৫; Track B স্বতন্ত্রভাবে নিশ্চিত করেছে ৩৭৮ = ২৬২+১১৬, যেখানে ১১৬ = ১১ redbox + ১০৫ অন্যান্য)। R12 canonical: ২৯৪ + ১৫ + ১০৫ = **৪১৪** ✓। R12 সংশোধিত: ২৯৪ + ৬৬ + ১০৫ = **৪৬৫** ✓। R11 সংশোধিত baseline: ২৬২ + ৭ + ১০৫ = **৩৭৪** (৩৭৮ নয় — §০ দেখুন)। Improved বনাম strict-এর +৪ offset সব সারিতে একই (improved scorer ৪টি শব্দে বেশি নমনীয়) — ৩৮২ = ৩৭৮+৪, ৪১৮ = ৪১৪+৪, ৪৬৯ = ৪৬৫+৪।

**এখনো বাকি ৩৩টি LINES শব্দ:** A-logo ১৬ (অস্পষ্ট/অনুপস্থিত কালি — segmentation দিয়ে ঠিক করা যায় না), E-cg-1 ৫ (E-ce-র মতো আরেকটি fused দুই-সারি কেস; পূর্ণ sub-band চিকিৎসা দরকার — Round 13-এর প্রস্তাব), C-insurance ৩, N1b ২, Issuing ২, N3 ২, B-demurrage ১, E-cg-2 ১, Inv ১। E-ce box-গুলো y-তে overlap করে (Consignee-র 'g' descender DHAKA-র x-range-এর ভেতরে) — inpainting ধাপের জন্য নোট করা আছে।

## ২. Track B — p3 span-level GT + পূর্ণ পাতা পুনঃগণনা (সম্পূর্ণ)

**p3 GT শূন্য থেকে তৈরি** (চোখ + CC মাপ, OCR নয়): ৫১ লাইন, **৩৮৪ শব্দ** — R5-এর ২৯৩-এর বিপরীতে। GT চোখে যাচাই করা: ১২টি overlay tile-এ (২× zoom, লাল GT box + নীল শব্দ লেবেল) ৩৮৪/৩৮৪ মিলেছে, ০টি unassigned CC, ০টি span overlap। ফাইল: `improve/round12/track-b/gt/rav-p3-ground-truth-r12.json` (মার্জে `merge-r12/gt/`-তে কপি আছে)।

**p3 পুনঃস্কোর** (Rounds ৯–১১-এর একই strict + improved নিয়ম, r10m seg, ৪৪৭ box): **strict ২৫০/৩৮৪ (৬৫.১%), improved ২৯২/৩৮৪ (৭৬.০%)**। Pre-R10 (R4 seg, ৪৬০ box): strict ২৪০/৩৮৪, improved ২৮০/৩৮৪।

**R10-এর p3 +৯ নিয়ে রায়: সংখ্যাটি ভুল, কিন্তু R10-এর নিজের সতর্কবাণী সঠিক ছিল।** আসলে ১২টি শব্দ ঠিক হয়েছিল, ৯টি নয় — SPLIT-তালিকার diff pre/post R10-তে ঠিক ১২টি fix দেখায় (g29 10138.43/5.80/58802.89, g31 10138.43/5.80/KG., g33 11.06.2026, g35 10138.43, g37 11459.00/2027.69/56775.2/58802.89, g38 58802.89), ০টি নতুন split। এটি R10 §৪.৩-এর সতর্কবাণী ("true gain could be +12") নিশ্চিত করে। কিন্তু হর (২৯৩) আর baseline (২৫৬) দুটোই ভুল ছিল: সত্য pre-R10 সঠিক ২৮০ improved / ২৪০ strict। সত্য R10 লাভ: **+১২ improved / +১০ strict**; সত্য p3 নির্ভুলতা ৭২.৯% → ৭৬.০% (improved), ৮৭.৪% → ৯০.৪% নয় যেমনটা ধরা হয়েছিল।

ত্রুটি-বিভাজন (r10m, improved): SPLIT ৬৬, MERGE ১৭, MISS ৯ (`ORIGINAL` + g03 `RAVIRAJ/FOILS/LIMITED` সম্পূর্ণ unboxed, আর BENEFICIARY লেবেলের মাথা seg-এ নেই সহ)। Strict scorer p3-তে improved-এর চেয়ে ৪২ শব্দ কম গোনে (p2-তে মাত্র ৪) — মিশ্র font size তার median-y নিয়ম ভাঙে, তাই **p3-র জন্য improved-ই সৎ মাপ**।

**পূর্ণ পাতা পুনঃগণনা (সংশোধিত baseline):**

| | R10 সত্য baseline | **R11 সত্য** | R11 দাবি |
|---|---|---|---|
| p2 | ৩২৩/৫০২ strict, ৩২৭ improved | ৩৭৮/৫০২, ৩৮২ improved | একই ✓ |
| p3 | ২৪০/৩৮৪ strict, ২৮০ improved | **২৫০/৩৮৪, ২৯২ improved** | ২৬৫/২৯৩ ✗ |
| **পূর্ণ পাতা** | **৫৬৩/৮৮৬ (৬৩.৫%) strict, ৬০৭/৮৮৬ (৬৮.৫%) improved** | **৬২৮/৮৮৬ (৭০.৯%) strict, ৬৭৪/৮৮৬ (৭৬.১%) improved** | ৬৪৩/৭৯৫ (৮০.৯%), ৬৪৭/৭৯৫ (৮১.৪%) ✗ |

R10→R11 সত্য লাভ: +৬৫ strict / +৬৭ improved (p2 +৫৫ + p3 +১০/+১২ — ঠিক মিলে যায়)।

**p2 spot-check (verdict গণনা, পুনরায় চালানো):** Pre-R11 verdicts: ৯৭ ok + ১০৮ correct = ২০৫, ১২২ miss। চূড়ান্ত: ১৫৪ ok + ১০৮ correct = **২৬২**, ৬৫ miss। ৫৭ flip = ৫৫ fix + ২ baseline সংশোধন; ২০৭ সত্য baseline; ৩৭৮ = ২৬২+১১৬ আর ৩২৩ = ২০৭+১১৬ — গাণিতিক হিসাব মিলে যায়। ভুল শুধু ৬৪৩/৭৯৫-এর p3 অর্ধেকে।

**সৎ সীমা:** R5-এর অঞ্চল-সীমানা ঠিকমতো পুনর্গঠন করা যায় না (কোনো শব্দতালিকা প্রকাশিত হয়নি) — +৯-এর রায় শব্দ-স্তরের diff-এর উপর দাঁড়িয়ে, অঞ্চল-গাণিতিকের উপর নয়। p3 seg-এ এখনো ৯২টি improved-miss আছে (বেশিরভাগ লম্বা-সংখ্যা split) — পরের রাউন্ডের কাজ, Track A/B-র নয়। Stamp (১৫ seg box) + logo (১) R5 রীতি অনুযায়ী FP হিসেবে গোনা হয়েছে, যদিও সেগুলো আসল কালি।

## ৩. Track C — verify_round2_300.py rebuild fix (সম্পূর্ণ)

**সিদ্ধান্ত: rebuild ধাপটি RETIRE করা হয়েছে (বিকল্প a), repoint নয়।** `verify_round2_300.py`-র ~৩০–৩৩ লাইন প্রতিটি রানে `build_page300.py` দিয়ে root p1 পাতা দুটি rebuild করত, কিছুই assert না করে (শুধু returncode)। Repoint প্রত্যাখ্যাত: merge builder-রা staging পাতা লেখে আর এই verifier root পাতা পড়ে, তাই repoint করলে হয় কিছুই করত না, নয়তো verifier-কে promoter বানিয়ে দিত — আর প্রতিটি রাউন্ডের merge dir-এর সঙ্গে জড়িয়ে যেত। Rebuild এখন সরানো হয়েছে (docstring আপডেট, অব্যবহৃত `subprocess`/`sys` import বাদ); ১৮টি চেক byte-identical। মূল ফাইল আর্কাইভ করা আছে `improve/round12/track-c/verify_round2_300.py.orig` (SHA `2ea6b32f…`)।

**প্রমাণ (মাপা, SHA + `cmp`):** Baseline (মূল verifier): fontfix ৪৩/৪৩, verify_round2 ১৮/১৮, repro300 PASS, manual ১০/১০ — কিন্তু p1 পাতা দুটি rewrite হয়েছিল (mtime ১১:২৬:৩৯/৪৪ UTC), byte একই ছিল শুধু R11 cleans sync করেছিল বলে। ফাঁদটি সুপ্ত ছিল, মৃত নয়। **Fix-এর পর, দুটি ধারাবাহিক রান:** verify_round2 ১৮/১৮ দুবার, fontfix ৪৩/৪৩, repro300 PASS, manual ১০/১০। Root p1 পাতার **mtime অপরিবর্তিত** — verifier আর কোনো live পাতা লেখে না। SHA দুটি পূর্ণ suite রানে byte-identical এবং R11-এর চূড়ান্ত SHA-র সঙ্গে একই (Aug p1 `bce37147…`, May p1 `d0948b0f…` ইত্যাদি); root p1 পাতা R11 staging পাতার সঙ্গে `cmp`-identical; cleans আর seg অপরিবর্তিত।

**Clamp wording: ভুল নয় — R10 verifier ছোঁয়া হয়নি।** R10-এর যে পাতাগুলো এটি চেক করে সেগুলোতে এখনো ০.৬০ floor baked-in (`f = Math.max(0.60 * fs0, …)`); wording সত্যিকারভাবে R10 আচরণ বর্ণনা করে। যেমন-আছে পুনরায় চালিয়ে মাপা: **৪৩/৪৩ PASS** (fs-ratio ০.৬৭/০.৬৬, width ১.০৮/১.০৯ — R11 Track C-র মাপা R10 baseline-এর সঙ্গে মিলেছে)। বর্তমান r11m verifier-এ ইতিমধ্যে সংশোধিত wording আছে; পুনরায় চালিয়ে মাপা: **৪৩/৪৩ PASS** (ceiling-only + width gate)। রেফারেন্স কপি আর্কাইভ করা আছে (`verify_may23_pages_r10m.py.orig`, SHA `733e42f2…`)।

**সৎ miss / পর্যবেক্ষণ:** Retire করায় auto-rebuild safety net চলে গেল: ভবিষ্যতে কোনো promotion root পাতা rebuild করতে ভুলে গেলে verify_round2_300 stale পাতায় pass করতে পারে। প্রস্তাবিত follow-up (বাস্তবায়ন করা হয়নি — check logic যোগ করত): একটি guard check যাতে পাতায় embedded WORDS root seg-এর সঙ্গে মেলে। Baseline rebuild root `heading-*.json`-ও rewrite করেছিল; মান R11 merge output-এর সঙ্গে একই, শুধু `"width_bold_override": []` key নেই (খালি list, r11m-builder-only) — ক্ষতিকর নয় এমন schema drift, পাতায় প্রভাব নেই। R10 verifier পুনরায় চালিয়ে `improve/round6/track-c/clips/`-এ তার নিজের ৮টি screenshot regenerate করেছে; summary JSON byte-identical (৪৩/৪৩); ২টি title clip byte-স্তরে আলাদা (rendering timing, non-gated eye-check aid; পুরনো byte backup করা হয়নি, শুধু SHA, তাই pixel মাত্রা মাপা যায়নি)। Shared DB কখনো খোলা হয়নি (দরকার ছিল না)। শুধু `verify_round2_300.py` বদলানো হয়েছে; কোনো live পাতা, seg, DB বা অন্য রিপোর্ট ছোঁয়া হয়নি।

## ৪. মার্জ — সিদ্ধান্ত

### ৪.১ সংশোধিত redbox GT canonical হিসেবে গৃহীত

**সিদ্ধান্ত: সংশোধিত redbox GT-কে canonical scorer হিসেবে গ্রহণ করা হলো।** কারণ:
1. R9 GT তিনভাবে মাপযোগ্যভাবে ভুল (border x৮৯৮–৯০৫ বনাম মাপা x১০০০–১০০৫; 'order' L8-এ বনাম মাপা L7; grey-Otsu fragment গ্রুপ যেমন 'control' ৪px — কোনো আসল word box ০.৯০ দুদিকে মেলাতে পারে না);
2. সমন্বয়কারীর নিজের পুনঃচালনা নিশ্চিত করেছে নতুন GT fixed seg-এ ৬৬/৬৬ আর পুরনো seg-এ ৭/৬৬ স্কোর করে, আর পুরনো GT ১৫/৬৬ আর ১১/৬৬ স্কোর করে — পুরনো GT fix-টি দেখতেই পায় না;
3. এটি প্রতিষ্ঠিত নজির অনুসরণ করে (R9 Description GT সংশোধন, R10 N5 GT সংশোধন)।

R9 GT + scorer আর্কাইভে অক্ষত আছে (`merge-r12/backup/redbox_score_r9_canonical.py` — GT LINES তালিকা scorer ফাইলের ভেতরেই hardcoded ছিল)। Canonical সংখ্যা হিসেবে এখন থেকে **সংশোধিত GT-র সংখ্যা** ব্যবহার হবে (p2 strict ৪৬৫/৫০২), আর পুরনো GT-র সংখ্যা (৪১৪/৫০২) সৎ তুলনার জন্য পাশাপাশি রাখা হবে।

### ৪.২ মার্জের নিজের ধরা — stale-seg ফাঁদ (আবার)

প্রথম identity probe-এ আমি ভুল seg ফাইল ব্যবহার করেছিলাম: `improve/round4/merge/segs/seg-{aug-p2,may-p2,may-p3}-300.json` — এগুলো **STALE** (৩০৬/৩১৩/৩০৬ শব্দ), আর live পাতায় embedded WORDS হলো r10m family (২৯৭/৩০৩/৩০১)। ফলে Aug p2 Lot-এর box [১৫০৪,৮৬০,১৫৬১,৮৮৮] আর WIDTH-এর box [১৮৯,১২৭৫,২৩৮,১৩০২] ছাপা হয়েছিল — দুটোই ভুল। ধরা পড়েছে পাতার embedded WORDS-এর সঙ্গে seg ফাইল মিলিয়ে দেখে (Aug p2: পাতা ২৯৭ = r10m ২৯৭ ✓, round4 ৩০৬ ✗; May p2: ৩০৩ = r10m ৩০৩ ✓; May p3: ৩০১ = r10m ৩০১ ✓)। **সঠিক seg দিয়ে probe আবার চালানো হয়েছে — ১৫/১৫, সব box R9/R6-এর রিপোর্ট করা box-এর সঙ্গে ঠিক মিলেছে।** শিক্ষা: probe-এর box-এ ভরসা করার আগে সবসময় যাচাই করতে হবে seg ফাইলটি পাতার embedded WORDS-এর সঙ্গে মেলে কি না।

### ৪.৩ মার্জ ডিরেক্টরি

`improve/round12/merge-r12/`: segs/ (১৯ ফাইল — r11m family + নতুন canonical `seg-rav-p2-r12m.json`, ৫৭৮ শব্দ), gt/ (নতুন canonical redbox GT + p3 GT + N5 r10 GT), pages/ (৫টি staging পাতা, root-এর সঙ্গে byte-identical), verifiers/ (r11m verifiers), scripts/ (r11m builder-দের merge-r12-এ repoint করা কপি — কোনো builder logic বদলানো হয়নি, কারণ PG seg বদলায়নি), backup/ (R9 canonical redbox scorer), clips/ (identity probe clips), shas/mtimes suite-before/after, verdicts-r12a.json, তিনটি track রিপোর্ট, heading-*-r12m.json (৫টি)।

**৫টি live পাতা rebuild করা হয়েছে** (r11m builder দিয়ে, merge-r12/pages/-এ) — **৫/৫-ই R11 promotion SHA-র সঙ্গে byte-identical** (Aug p1 bce37147, Aug p2 f4f72713, May p1 d0948b0f, May p2 539995a9, May p3 8587be86)। PG পাতায় কোনো পরিবর্তন নেই — আশা অনুযায়ী, কারণ Round 12-এ কোনো PG seg বদলায়নি (Track A শুধু Rav p2 seg বদলেছে, Track B শুধু p3 GT বানিয়েছে, Track C শুধু verifier ঠিক করেছে)। Root পাতা promotion-এর দরকার হয়নি।

## ৫. যাচাই সারণি (সমন্বয়কারীর নিজের পুনঃচালনা)

| চেক | ফল |
|---|---|
| fontfix_verify300.py | **৪৩/৪৩ PASS** |
| verify_round2_300.py (fixed rebuild) | **১৮/১৮ PASS** — root পাতার SHA + mtime suite-র আগে/পরে অপরিবর্তিত |
| repro300.py | **PASS** — ২টি edited span, exact text, .done, no doubling |
| manual_proof300.py | **১০/১০ PASS** |
| identity probe (৫ পাতা, সঠিক seg) | **১৫/১৫** — Lot+WIDTH+Hard × ৫, চোখে যাচাই করা clip সহ |
| write-back | **৪১/৪১ + ৪০/৪০, FAILURES: none** |
| Track D staging | **৪৮/৪৮** ([PASS] লাইন ৪৮, FAILURES: none) |
| Track C (R5) staging | **৭৪/৭৪** ([PASS] লাইন ৭৪, FAILURES: none) |
| May multipage | **৫৯/৫৯** ([PASS] লাইন ৫৯, FAILURES: none) |
| May p2/p3 (r11m verifier) | **৪৩/৪৩ PASS** |
| sqlcipher_test.py | **১৫/১৫** ([PASS] লাইন ১৫, FAILURES: none) |
| keymgmt_proof.py | **২৫/২৫** ([PASS] লাইন ২৫, FAILURES: none) |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** (staging verify_save_label.py ৩৪/৩৪ — R8 staging পাতা) |
| Aug p2 (r10m verifier, root) | **১৬/১৬** (R8 script ১৫/১৫ — নিজের R8 staging পাতা, stale artifact) |
| heading R1 (check_heading_r11.py) | **PASS ১৪/১৪ × ৩ family** (TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০) |
| sample rows (r10m) | **৫১৮/৫১৮, ০ extra** |
| N5 (r10 scorer) | **৭৭/৮১ strict, ৮১/৮১ improved** — অপরিবর্তিত |
| Description (r10 GT) | **৬৯/৬৯, wrong ০** — অপরিবর্তিত |
| redbox নতুন scorer (merge r12m seg) | **৬৬/৬৬** (r11m seg baseline ৭/৬৬) |
| redbox canonical R9 scorer (merge r12m seg) | **১৫/৬৬** (r11m seg baseline ১১/৬৬) |
| p3 re-score (merge GT, r10m seg) | **strict ২৫০/৩৮৪ (৬৫.১%), improved ২৯২/৩৮৪ (৭৬.০%)** |
| LINES verdicts (merge copy) | **২৯৪/৩২৭** (ok ১৮৬ + correct ১০৮, miss ৩৩) |
| live পাতা rebuild | **৫/৫ byte-identical** R11 promotion SHA-র সঙ্গে |
| shared DB | **SHA 1c065457… অপরিবর্তিত, ২০ audit entry, chain linked, ৭ delivery** |

**দুটি গণনা-স্পষ্টকরণ (R11 §১৩৭-এর মতো):** (ক) save→label ৯০/৯০ হলো LIVE verifier (১৮ চেক/পাতা × ৫); staging verify_save_label.py দেয় ৩৪/৩৪ (R8 staging পাতায়)। (খ) Aug p2 ১৬/১৬ হলো R10 merge verifier root পাতায়; R8 script `verify_aug2_page.py` দেয় ১৫/১৫ কিন্তু সেটি নিজের R8 staging পাতা (৩০১ শব্দ, r7m seg) চেক করে — R12-এ অপরিবর্তিত stale artifact, root পাতা নয়।

**দুটি legacy script ফাঁদ (নোট, ব্যর্থতা নয়):** `check_titles_h2_r9m.py` আর `sample_rows_r11m.py` suffix ছাড়া চালালে stale r6base seg খোঁজে (`seg-aug-p1-r6base.json` নেই বলে FileNotFoundError) — r10m suffix দিলে sample চলে (৫১৮/৫১৮); heading-এর জন্য canonical যাচাই হলো `check_heading_r11.py` (PASS ১৪/১৪ × ৩)।

**Round 3-র পুরনো verify_rebuild_300.py এখনো তার ৪টি known ink-IoU fail দেখায়** (v1 staging artifact, ২৯/৩৩) — superseded artifact, regression নয়; বর্তমান R10 work/verify_rebuild_300.py ৪০/৪০ PASS।

## ৬. সৎ miss ও এখনো খোলা

- **Raviraj p2:** ৩৩টি LINES শব্দ বাকি (A-logo ১৬, E-cg-1 ৫, C-insurance ৩, N1b ২, Issuing ২, N3 ২, B-demurrage ১, E-cg-2 ১, Inv ১)। E-cg-1-এর জন্য পূর্ণ sub-band চিকিৎসা দরকার — Round 13-এর প্রার্থী।
- **Raviraj p3:** ৯২টি improved-miss (বেশিরভাগ লম্বা-সংখ্যা split) — পরের রাউন্ডের কাজ।
- **Redbox L5 'and':** শুধু 'a' বেঁচে আছে ('nd'-এর কালি নেই) — গোনা হয়েছে, ফ্ল্যাগ করা আছে।
- **E-ce box overlap:** fused সারি জুড়ে y-overlap (descender) — inpainting ধাপের জন্য নোট করা।
- **Guard check বাস্তবায়ন হয়নি:** পাতায় embedded WORDS root seg-এর সঙ্গে মেলে কি না — Track C-র প্রস্তাবিত follow-up (retired rebuild-এর safety net-এর বদলে)।
- **আগের মতোই খোলা:** print calibration (কারখানার প্রিন্টার), US patent আইনি যাচাই (উকিলের কাজ), DBNet swap স্থগিত (KEEP CLASSICAL সিদ্ধান্ত), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` পাওয়া যায়নি, PDF-এর অন্য ২৫ পাতা শুধু contact-sheet দেখা হয়েছে, Lot-anchor threshold অন্য template-এ পুনঃযাচাই দরকার।

## ৭. Round 13-এর প্রস্তাব

1. **E-cg-1 ৫** — E-ce-র মতো fused দুই-সারি কেস, পূর্ণ sub-band চিকিৎসা।
2. **p3-র ৯২ improved-miss** — লম্বা-সংখ্যা split (Rule D-র পরের ধাপ)।
3. **Guard check** — পাতায় embedded WORDS বনাম root seg (Track C follow-up)।
4. **Lot-anchor threshold** অন্য template-এ পুনঃযাচাই।

---
*সমন্বয়কারীর নোট: এই রিপোর্টের প্রতিটি সংখ্যা কোড চালিয়ে মাপা — কোনো সংখ্যা দাবি করা হয়নি। মার্জের নিজের দুটি সংশোধন (§০-র +৯১ আর §৪.২-র stale-seg ফাঁদ) রিপোর্টে খোলাখুলিভাবে লেখা আছে।*
