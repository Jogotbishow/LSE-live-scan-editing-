# LSE Round 13 রিপোর্ট

**তারিখ:** ২০২৬-১১-০৭ · **স্থান:** `scan-paper/improve/` · **মার্জ ডিরেক্টরি:** `improve/round13/merge-r13/`
**তিন ট্র্যাক সমান্তরালে, একটিই কোঅর্ডিনেটর (এই সেশন), কোনো scheduled job নয়।**

## ০. এক নজরে

| মাপ | R12 | **R13 (মার্জ)** |
|---|---|---|
| Raviraj p2 LINES | ২৯৪/৩২৭ | **৩১১/৩২৭ (+১৭)** |
| p2 strict (ক্যানোনিক্যাল redbox) | ৪১৪/৫০২ (৮২.৫%) | **৪৩১/৫০২ (৮৫.৯%)** |
| p2 strict (সংশোধিত redbox GT) | ৪৬৫/৫০২ (৯২.৬%) | **৪৮২/৫০২ (৯৬.০%)** |
| p2 improved (ক্যানোনিক্যাল / সংশোধিত) | ৪১৮ / ৪৬৯ | **৪৩৫ / ৪৮৬** |
| p3 strict | ২৫০/৩৮৪ (৬৫.১%) | **৩৩৪/৩৮৪ (৮৭.০%)** |
| p3 improved | ২৯২/৩৮৪ (৭৬.০%) | **৩৮৪/৩৮৪ (১০০.০%)** |
| p3 SPLIT / MERGE / MISS | ৬৬ / ১৭ / ৯ | **০ / ০ / ০** |
| **পূর্ণ পাতা strict (ক্যানোনিক্যাল, হর ৮৮৬)** | ৬৬৪/৮৮৬ (৭৪.৯%) | **৭৬৫/৮৮৬ (৮৬.৩%)** |
| **পূর্ণ পাতা strict (সংশোধিত GT)** | ৭১৫/৮৮৬ (৮০.৭%) | **৮১৬/৮৮৬ (৯২.১%)** |
| **পূর্ণ পাতা improved (ক্যানোনিক্যাল)** | ৭১০/৮৮৬ (৮০.১%) | **৮১৯/৮৮৬ (৯২.৪%)** |
| **পূর্ণ পাতা improved (সংশোধিত GT)** | ৭৬১/৮৮৬ (৮৫.৯%) | **৮৭০/৮৮৬ (৯৮.২%)** |
| False merge (দুই ট্র্যাকেই) | ০ | **০** |
| Guard check (নতুন) | প্রস্তাবমাত্র | **৫/৫ PASS, stale ৩/৩ FAIL — এখন মার্জের অংশ** |
| Lot-anchor ০.০৩৬ | PG ১৪ পাতায় টিকে | **১৪/১৪, gap +০.০১২৯৫৩, LOPO ১৪/১৪ — রায়: HOLD** |
| Live পাতা (৫টি) | R11 SHA-র সঙ্গে identical | **৫/৫ byte-identical — promotion লাগেনি** |
| N5 / Description | ৭৭/৮১ strict, ৮১/৮১ improved / ৬৯/৬৯ | **অপরিবর্তিত — কোনো regression নেই** |
| Redbox | ৬৬/৬৬ (সংশোধিত), ১৫/৬৬ (R9) | **অপরিবর্তিত** |

**লাভের হিসাব:** strict +১০১ (দুই redbox গণনাতেই), improved +১০৯। p2-তে +১৭ (Track A), p3-তে strict +৮৪ / improved +৯২ (Track B)। p2 strict-এর গাণিতিক যাচাই (R12 §১-এর সূত্র: LINES-সঠিক + redbox-সঠিক + অন্যান্য-outside-সঠিক ১০৫): ক্যানোনিক্যাল ৩১১ + ১৫ + ১০৫ = **৪৩১** ✓; সংশোধিত ৩১১ + ৬৬ + ১০৫ = **৪৮২** ✓ — মার্জের নিজের পুনঃচালনায় LINES ৩১১ আর redbox ৬৬/১৫ দুটোই মিলেছে।

## ১. Track A — p2-র বাকি ১৭টি LINES miss (সম্পূর্ণ)

**নতুন seg:** `improve/round13/track-a/seg-rav-p2-r13m.json` (৫৫৫ শব্দ; r12m ছিল ৫৭৮; SHA `bf00918c…`)।
**পদ্ধতি:** ৪০টি fragment বাক্স সরিয়ে ১৭টি হাতে-মাপা কালি-সীমা বাক্স (`r13a_gt.json`, Otsu tight-band + labelled overlay চোখে যাচাই ১৭/১৭)।

**নির্ণয় — একটাই ধরন, fragmentation:** কালি একটানা (শব্দের ভেতরে ফাঁক ≤৭px), কিন্তু seg ১–৭px ফাঁকে ভেঙে গেছে, মাঝের ছোট কালি (apostrophe, hyphen, comma, '17', 'ou', 'i', 'e', period) কোনো বাক্সেই ছিল না। অন্ধ gap-নিয়মে ঠিক করা যাবে না — Amount→To কালি-ফাঁক মাত্র ৬px, অথচ SURVEY→NO ৮px (সেটি আলাদা শব্দ)।

**প্রতি ধরনের ফল (সব ১০০%):** E-cg-1 ৭/৭, E-cg-2 ১০/১০, C-insurance ৩৪/৩৪, N1b-corporate ৩৭/৩৭, Issuing ২০/২০, N3 ২৫/২৫, B-demurrage ১৮/১৮, Inv ১০/১০। **LINES ২৯৪ → ৩১১/৩২৭।** False merge ০ (overlap যাচাই + diff: ঠিক ৪০টি সরানো, ১৭টি যোগ, আর কোনো পুরনো বাক্স হারায়নি)।

**R12-র দুটি সংশোধন:** (ক) E-cg-1 একটিমাত্র সারি y১২৮৭–১৩৩১-এ — R12-র "y১৩৬০–১৩৯০ দুই-সারি" ভুল ছিল (সেটি GSTIN সারি, E-cg-3); দুই-সারি ফিউশন এখানে ছিলই না। (খ) ভার্ডিক্ট-নোটের দুটি ভুল: 'as:'-এর "no box" — box ৮৩ (x৪৬৭–৫৭৮) আছেই; U60231…-এর "শুধু rule box (FP)" — box ৯২ অক্ষরগুলোই ঢাকে।

### ১.১ সবচেয়ে বড় সংশোধন — A-logo "কালি নেই" ধারণাটি ভুল

R12 বলেছিল A-logo-র ১৬টি শব্দে কালি নেই বলে segmentation ঠিক করতে পারবে না। **মাপা প্রমাণ বলছে উল্টো — ১৬টির একটিতেও কালি কম নয়।** Track A প্রতিটি শব্দের expected অঞ্চলে গাঢ় পিক্সেল মেপেছে (control শব্দের সমান বা বেশি), আর কোঅর্ডিনেটর স্বতন্ত্রভাবে যাচাই করেছে:

- **M (logo অক্ষর):** CC ঠিক (৪০০,২৭৪,১১২,১০৯), area ৯৪০৯, কেন্দ্র (৪৫৫,৩২৭) — `segment.py`-র LOGO exclusion zone (১৫০,১২০,৫১০,৪৫০)-এর ভেতরে বলে বাদ পড়েছে। কোঅর্ডিনেটরের নিজের মাপে M-এর bbox-এ ৭২.৬% পিক্সেল <১৮০ (Track A-র ৪৫.৬% — অঞ্চল-সংজ্ঞার পার্থক্য, সিদ্ধান্ত একই: কালি প্রচুর)।
- **SERVICE/REG./NO./AADCM0917AST001:** অক্ষরগুলো এক দৈত্য CC (৩৪৭,৫৫৩,৬৫৬,৩২১), area ১৯৩২২, hh=৩২১ > ১৮০ ফিল্টারে বাদ — টেবিল রুল + নিচের SCHEDULE লাইনের সঙ্গে জুড়ে গেছে।
- **26-05-2006/•/CIN:/U60231…:** নিজের CC আছে, merged box ৯২-তে ঢাকা।
- **Nothing's/MAA/ANNAPURNA/TRANSPORT/AGENCY:** সাদা ভাঙা/জোড়া — একই merge-পদ্ধতিতে ঠিক করা যায়।

**সৎ শ্রেণিবিভাগ (পরের রাউন্ডের জন্য):** (ক) merge-পদ্ধতিতে ঠিক করা যায় — Nothing's, MAA, ANNAPURNA, TRANSPORT, AGENCY (৫) + known/as: un-merge ও y-বাড়ানো (২); (খ) দৈত্য-CC rescue লাগবে — SERVICE, REG., NO., AADCM0917AST001 (৪); (গ) box ৯২ ভাঙা — 26-05-2006, •, CIN:, U60231… (৪); (ঘ) LOGO-zone সিদ্ধান্ত — M (১)। এই রাউন্ডের scope-এর বাইরে বলে ছোঁয়া হয়নি — সিদ্ধান্ত বাকি। **"A-logo segmentation দিয়ে ঠিক করা যায় না" আর সত্য নয় — ঠিক করার পথ মাপা আছে, শুধু করা হয়নি।**

## ২. Track B — p3-র ৯২ improved-miss (সম্পূর্ণ)

**নতুন seg:** `improve/round13/track-b/seg-rav-p3-r13b.json` (৪০০ বাক্স; r10m ছিল ৪৪৭; SHA `fe5fa6df150e…`)।
**পদ্ধতি:** R11 Track B-র Rule D পুনঃব্যবহার + বাড়তি (EXTEND, split+extend হাইব্রিড, ADD-এ y-নিয়ম)। প্রতিটি নতুন বাক্সে apply-time গেট: improved নিয়মে ঠিক একটি GT শব্দের সঙ্গে মেলে, সেই শব্দ ৯২টি intended miss-এর একটি — **gate reject ০**।

**শ্রেণি অনুযায়ী ফল (৯২/৯২):** MERGE ৩৯ (দীর্ঘ সংখ্যা/কোড ১৭, ঠিকানা ৫, বড়-অক্ষরের শব্দ ১২, ছোট টোকেন ৫), EXTEND ২৭ (কাটা trailing `.`/`,`/`:` ২২ + বড় ৫), SPLIT-BOX ১৭ শব্দ / ১০ বাক্স, ADD ৯ (ORIGINAL + শিরোনাম ৩ + ক্ষুদ্র বিরামচিহ্ন ৫)। বাক্স-সংখ্যা ৪৪৭ → ৪০০ (সরানো ১৩৯, যোগ ৯২)। **SPLIT/MERGE/MISS ০/০/০, FP ১৫৫ → ১৬** (stamp ১৫ + logo ১, R5 রীতি অনুযায়ী)।

**False merge ০ — তিনটি স্বতন্ত্র প্রমাণ:** apply-time গেট reject ০; regression যাচাই — improved-এ আগে ঠিক থাকা ২৯২টির ০টি মিস হয়নি; diff যাচাই — সরানো ১৩৯টির সবগুলো log-input, যোগ করা ৯২টির সবগুলো log-output (একটি ব্যতিক্রম: intermediate QUANTITY-tail piece, ধাপ-১-এ তৈরি হয়ে ধাপ-২-এর MERGE-এ খরচ — log-এ দুদিকেই আছে, প্রত্যাশিত)। **GT পরিবর্তন: ০টি।** চোখে যাচাই: ৩৩টি overlay (২×) + ৫টি ৬× zoom — ৯২টি শব্দের প্রতিটি দেখে মেলানো।

**সৎ হিসাব — strict-এর ২টি regression ও ১৪টি side-effect gain:** g12 `IRC` ও g14 `BIN` strict-এ ফেল করেছে — বাক্স byte-অপরিবর্তিত, improved-এ ঠিক; কারণ strict median-y-র see-saw (fragment জোড়ায় ডান-কলামের বড় সংখ্যার টুকরো কমেছে, median বাঁ-কলামের ছোট ফন্টের দিকে সরেছে)। Median-কে টেনে ফেরানো scorer-gaming হতো, তাই করা হয়নি। উল্টোদিকে ১৪টি শব্দ (g11 MOHAKALI/DOHS,/DHAKA/1206,; g12 FACTORY:/ADHURIA,/BHULTA,/RUPGANJ,/NARAYANGANJ,/BANGLADESH.; g14 SHAHAJALAL/ISLAMI/BANK/PLC) median-সরার উপজাতে strict-এ পাস করেছে — ফিক্সের কৃতিত্ব নয়। তাই strict লাভ: gross নতুন ঠিক ৮৬ − regression ২ = **net +৮৪**। একটি ধরা-পড়া regression ঠিক করা হয়েছে: g00 ORIGINAL-এর tight y median hijack করে FOILS-কে ফেল করিয়েছিল — band y [259,297] দিয়ে ঠিক (strict ৩৩৩ → ৩৩৪)।

**p3 strict-এ বাকি ৫০টি:** ২০টি এই রাউন্ডের fixed শব্দ (median-সীমা — ক্ষুদ্র বিরামচিহ্ন ৫ + মিশ্র-ফন্ট লাইনের বড় টোকেন ১৫) + ৩০টি আগে থেকেই strict-miss ছিল। বাক্স অপরিবর্তিতভাবে সঠিক; R12-এর রায় বহাল — **p3-র জন্য improved-ই সৎ মাপ, strict scorer অবিশ্বস্তই আছে।**

## ৩. Track C — Guard check + Lot-anchor পুনঃযাচাই (সম্পূর্ণ)

### ৩.১ Guard check — এখন মার্জের অংশ

**স্ক্রিপ্ট:** `improve/round13/merge-r13/scripts/guard_check.py` (+ `identity_pg.json`) — Track C-র `guard_check.py`-র কপি। পাঁচটি চেক: C1 count, C2 ordered (ক্রমসহ পূর্ণ তুলনা), C3 multiset, C4 spot (row label + box, ~২১–২৬টি নমুনা), C5 identity (Lot/WIDTH exact box; Hard nearest-centre ≤১৮px)। Exit ০ = PASS, ১ = FAIL, ২ = error। `--mode full` (ডিফল্ট) সব চেক চালায়; `--mode spot-only` শুধু C1+C4(+C5) — production মোড নয়।

**প্রমাণ (Track C, `run_guard_proof.py`, ১৪ কেস, exit ০):** সঠিক seg ৫/৫ PASS; stale round4 seg ৩/৩ FAIL (২৯৭/৩০৬, ৩০৩/৩১৩, ৩০১/৩০৬); সূক্ষ্ম mutation M2 (৩টি box +৬px, নমুনার বাইরে) আর M3 (২টি box অদলবদল) **spot-only-তে PASS করে যায়, full-এ FAIL** — প্রমাণিত: **count+spot একা যথেষ্ট নয়, production-এ সবসময় full মোড।** M4 (নমুনার ভেতরে বদল) দুই মোডেই FAIL (control)।

**মার্জের নিজের পুনঃচালনা (Guard-মিলিয়ে, তারপর probe):** ৫টি live পাতা × merge-r13 seg — **৫/৫ PASS, exit ০** (Aug p1 ৩০২/৩০২, Aug p2 ২৯৭/২৯৭, May p1 ৩০২/৩০২, May p2 ৩০৩/৩০৩, May p3 ৩০১/৩০১; spot ২৪/২৪, ২৬/২৬, ২৪/২৪, ২৪/২৪, ২১/২১; identity সব পাতায় PASS)। Stale round4 seg পুনঃচালনা: **FAIL, exit ১** (২৯৭/৩০৬, spot ০/২৬) — R12-র ফাঁদটি এখন যান্ত্রিকভাবে ধরা পড়ে। রিপোর্ট: `merge-r13/guard-*.json` (৬টি)।

**পথে পাওয়া সংশোধন:** probe-এর Hard box [2101,1211,2177,1241] শুধু Aug p2-তেই exact — অন্য ৪ পাতায় আসল box ১০–১৫px দূরে (Aug p1 ১০.৩px, May p1 ১৫.০px, May p2 ১৫.৪px, May p3 ১৪.৪px)। Guard-এ Hard "near" entry হিসেবে আছে (seg-nearest আর page-nearest একই box হতে হবে, ≤১৮px)। এই সংশোধন ছাড়া Guard সঠিক seg-কেই ভুল বলত।

**Guard কোথায় বসবে (Track C-র সুপারিশ, গৃহীত):** (১) probe flow-র প্রথম ধাপ — Guard FAIL হলে probe শুরুই হবে না; (২) merge checklist-এ Guard verdict (পাতা × seg, exit code সহ); (৩) promotion-এর আগে Guard দিয়ে promotion-এর seg root পাতার সঙ্গে মেলানো — R12 Track C-র retired rebuild-এর safety net-এর বদলে এটাই নতুন net; (৪) নতুন template-এ identity entry template-এর সঙ্গে freeze করতে হবে। **Residual risk (সৎ নোট):** Guard মিল যাচাই করে, সত্য নয় — পাতা আর seg দুটোই একই ভুল box ধরলে Guard PASS বলবে; এর প্রতিকার builder/seg-এর নিজের যাচাই।

### ৩.২ Lot-anchor ০.০৩৬ — HOLD + fallback বহাল

**মার্জের নিজের পুনঃচালনা (`lot_anchor_r13c.py`) Track C-র সঙ্গে হুবহু মিলেছে:** PG ১৪ পাতা — Aug lotdiff ০.০১১৭৫৭–০.০২৯৪০৬ (n=৮), May ০.০৪২৩৫৯–০.০৬৩৪৪৮ (n=৬); **gap +০.০১২৯৫৩**, midpoint ০.০৩৫৮৮২ (নিয়মের ০.০৩৬ থেকে মাত্র ০.০০০১১৮ দূরে); **নিয়ম ০.০৩৬ সঠিক ১৪/১৪, LOPO ১৪/১৪**; সবচেয়ে পাতলা margin **০.০০৬৩৫৯** (May p6, bold দিকে) আর ০.০০৬৫৯৪ (Aug p2, regular দিকে); r12m PG seg r10m-এর সঙ্গে **১৪/১৪ box-identical**; R11-র ১৪টি lotdiff হুবহু reproduce।

**Raviraj-এ নিয়মটি প্রযোজ্য নয় (মাপা, জোর করে নয়):** exact LOT/WIDTH/THICKNESS/MICRON/GSM/SIZE/LENGTH token **০/০** দুই পাতাতেই (একমাত্র 'LOT' হিট PLOT-এর ভেতরে); live পাতা ০; decided bold/regular শব্দ ০। p3-র পণ্য-টেবিলে সংখ্যামান আছে (g29: 10138.43 / 5.80 / 58802.89), কিন্তু কোনো same-table known-regular anchor নেই, কোনোটিরই decided status নেই — diff সংখ্যা বের করা যেত, কিন্তু সেটি পরীক্ষা হতো না। **অন্য পরিবার (Tottel/FUNSD/SROIE/Shields): কেউই তুলনীয় নয়** — Lot/WIDTH spec টেবিল নেই। **Validation set এখনো PG-only: ১টি template, ২টি document, ১৪টি পাতা।**

**রায়: HOLD + fallback বহাল, margin চওড়া নয়।** ০.০৩৬ টিকে আছে, threshold সরানোর কারণ নেই; কিন্তু সবচেয়ে পাতলা margin ~০.০০৬৪ — পুরনো ratio-নিয়মের knife-edge ০.০০০১৫৯-এর ৪১ গুণ হলেও absolute অর্থে পাতলা; তথ্য ছাড়া margin বদলানো আন্দাজে বদলানো। Lot anchor না থাকলে (বা Lot নিজে bold হলে) ratio-নিয়মে ফেরা — fallback বাধ্যতামূলক। **পরের template-এ promotion-এর আগে সেই template-এর WIDTH-সম শব্দের bold/regular GT আগে decide করতে হবে, তারপর lotdiff মেপে threshold পুনঃযাচাই — প্রয়োজনে per-template threshold। PG-র ০.০৩৬ অন্য template-এ অন্ধভাবে প্রয়োগ করা যাবে না।** সৎ সীমা: May p4–p6 আর Aug p3–p8-এর bold/regular GT এখনো same-document অনুমান — p1–p3 live পাতার সিদ্ধান্ত ছাড়া বাকি ৯ পাতার GT page-by-page decided নয়।

## ৪. মার্জ — একটি সামঞ্জস্যপূর্ণ v8 পাতা সেট

**Seg পরিবার (merge-r13/segs/):** r12m PG seg ১৪টি (অপরিবর্তিত) + Track A `seg-rav-p2-r13m.json` (৫৫৫ শব্দ) + Track B `seg-rav-p3-r13b.json` (৪০০ বাক্স)। দুই ট্র্যাক ভিন্ন ফাইল বদলেছে (p2 বনাম p3) — কোনো সংঘাত নেই। PG seg ছোঁয়া হয়নি। মার্জ কপি byte-identical (`cmp` পাস)।

**Live পাতা rebuild (r13m builder, merge-r13/pages/-এ): ৫/৫ byte-identical** root-এর সঙ্গে (Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2 `539995a9…`, May p3 `8587be86…`)। **PG পাতায় কোনো পরিবর্তন নেই — promotion লাগেনি, re-upload লাগবে না।** Heading JSON ৫/৫ R12-র সঙ্গে identical। (May23 builder-এ পাতা-আর্গুমেন্ট দিতে হয় — প্রথম রানে শুধু may-p2 তৈরি হয়েছিল, `may3` দিয়ে may-p3 আলাদা করে বানানো হয়েছে।)

**মার্জের নিজের পুনঃমাপ (track রিপোর্টের সংখ্যা নয়, merge ফাইলে চালানো):** LINES ৩১১/৩২৭ (`rescore_lines_r13m.py`); redbox নতুন scorer ৬৬/৬৬, R9 canonical ১৫/৬৬; p3 strict ৩৩৪/৩৮৪, improved ৩৮৪/৩৮৪, SPLIT/MERGE/MISS ০, FP ১৬; N5 ৭৭/৮১ strict, ৮১/৮১ improved; Description (r10 GT) ৬৯/৬৯, wrong ০; Lot-anchor ১৪/১৪ (উপরে §৩.২); Guard ৫/৫ PASS + stale FAIL। **পূর্ণ পাতা (হর ৮৮৬): strict ক্যানোনিক্যাল ৭৬৫, সংশোধিত ৮১৬; improved ক্যানোনিক্যাল ৮১৯, সংশোধিত ৮৭০।**

**Description-নোট (সৎ স্পষ্টকরণ):** পুরনো R9 GT দিয়ে scorer দেয় ৬৩/৬৯ (৬টি ভুল: L3:QUANTITY, UNIT, PRICE, USD, 5.80/KG.., L4:CPT) — কিন্তু r12m আর r13m **দুটোতেই একই ৬৩/৬৯**, অর্থাৎ regression নয়, GT-সংস্করণের পার্থক্য। Canonical r10 GT-তে ৬৯/৬৯ দুটোতেই।

## ৫. যাচাই সারণি (কোঅর্ডিনেটরের নিজের পুনঃচালনা)

| চেক | ফল |
|---|---|
| fontfix_verify300.py | **৪৩/৪৩ PASS** |
| verify_round2_300.py (rebuild RETIRED) | **১৮/১৮ PASS × ২ ধারাবাহিক রান** — root পাতার SHA + mtime suite-র আগে/পরে অপরিবর্তিত |
| repro300.py | **PASS** — ২টি edited span, exact text, .done, no doubling |
| manual_proof300.py | **১০/১০ PASS** |
| identity probe (৫ পাতা, Guard-মিলিয়ে নেওয়া seg) | **১৫/১৫** — Lot+WIDTH+Hard × ৫, চোখে যাচাই করা clip সহ (Aug p2 WIDTH ৭৭৬.৫ পরিষ্কার, Hard অক্ষত) |
| Guard check (নতুন, full মোড) | **৫/৫ PASS, exit ০**; stale round4 seg **FAIL, exit ১** |
| write-back | **৪১/৪১ + ৪০/৪০, FAILURES: none** |
| Track D staging | **৪৮/৪৮** ([PASS] লাইন ৪৮, FAILURES: none) |
| Track C (R5) staging | **৭৪/৭৪** ([PASS] লাইন ৭৪, FAILURES: none) |
| May multipage | **৫৯/৫৯** ([PASS] লাইন ৫৯, FAILURES: none) |
| May p2/p3 (r11m verifier) | **৪৩/৪৩ PASS** |
| sqlcipher_test.py | **১৫/১৫** ([PASS] লাইন ১৫, FAILURES: none) |
| keymgmt_proof.py | **২৫/২৫** ([PASS] লাইন ২৫, FAILURES: none) |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** |
| Aug p2 (r10m verifier, root) | **১৬/১৬** (Hard neighbour untouched) |
| heading R1 (check_heading_r11.py) | **PASS ১৪/১৪ × ৩ family** (TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০; control-এ H1-diff ২ প্রত্যাশিত) |
| sample rows (r10m) | **৫১৮/৫১৮, ০ extra** |
| N5 (r10 scorer, merge seg) | **৭৭/৮১ strict, ৮১/৮১ improved** — অপরিবর্তিত |
| Description (r10 GT, merge seg) | **৬৯/৬৯, wrong ০** — অপরিবর্তিত |
| redbox নতুন scorer (merge r13m seg) | **৬৬/৬৬** |
| redbox canonical R9 scorer (merge r13m seg) | **১৫/৬৬** |
| p3 re-score (merge GT, merge r13b seg) | **strict ৩৩৪/৩৮৪ (৮৭.০%), improved ৩৮৪/৩৮৪ (১০০.০%)** |
| LINES verdicts (merge copy) | **৩১১/৩২৭** |
| Lot-anchor (merge পুনঃচালনা) | **১৪/১৪, gap +০.০১২৯৫৩, LOPO ১৪/১৪, thinnest ০.০০৬৩৫৯** |
| live পাতা rebuild | **৫/৫ byte-identical** R11/R12 promotion SHA-র সঙ্গে |
| shared DB (read-only) | **SHA 1c065457… অপরিবর্তিত, ২০ audit entry, chain linked, ৭ delivery (LSE-0001–0007)** |

**পরিবেশ-নোট:** Track C-র কাজে সিস্টেম `python3`-এ `cv2` ছিল না বলে `pip install --user opencv-python-headless` চালাতে হয়েছে — side effect হিসেবে numpy ১.২৬.৪ → ২.৫.৪ (মাপে প্রভাব নেই — R11-র ১৪টি lotdiff হুবহু reproduce হয়েছে, আর মার্জের পুরো suite venv থেকে চালিয়ে পাস করেছে)। এটি track dir-এর বাইরে একমাত্র পরিবেশ-পরিবর্তন।

**Round 3-র পুরনো verify_rebuild_300.py এখনো তার ৪টি known ink-IoU fail দেখায়** (v1 staging artifact, ২৯/৩৩) — superseded artifact, regression নয়; বর্তমান R10 work/verify_rebuild_300.py ৪০/৪০ PASS (উপরে)।

## ৬. সৎ miss ও এখনো খোলা

- **A-logo ১৬** — §১.১-এর শ্রেণিবিভাগ অনুযায়ী (ক) ৫+২ merge-পদ্ধতিতে, (খ) ৪ দৈত্য-CC rescue, (গ) ৪ box ৯২ ভাঙা, (ঘ) ১ LOGO-zone সিদ্ধান্ত। "কালি নেই" ভুল প্রমাণিত হয়েছে; ঠিক করার পথ মাপা আছে — পরের রাউন্ডের কাজ।
- **p3 strict ৫০টি** — median-y নিয়মের সীমা (§২); strict scorer বদলানো ছাড়া ঠিক করা যাবে না, আর median-কে টেনে ফেরানো scorer-gaming হবে। p3-র জন্য improved-ই সৎ মাপ।
- **p2-র বাকি ৩৩টি LINES miss-এর মধ্যে ১৬টিই A-logo** — p2 strict ক্যানোনিক্যাল ৪৩১/৫০২-এর বাইরে বাকি ৭১টির বড় অংশই এখন A-logo + redbox-বহির্ভূত অঞ্চলের strict-সীমা।
- **Merge-পদ্ধতি সাধারণ নিয়মে আনা যাবে না** (Track A-র সুপারিশ): শব্দের ভেতরের ফাঁক ≤৭px বনাম পাশের শব্দের ফাঁক ≥৬px — Amount→To-র ৬px দেখায় অন্ধ threshold বিপজ্জনক; হাতে-নির্দিষ্ট GT স্প্যানই নিরাপদ।
- **Lot-anchor PG-only** — নতুন template-এ GT-decided পুনঃযাচাই ছাড়া ০.০৩৬ প্রয়োগ করা যাবে না (§৩.২)।
- **আগের মতোই খোলা:** print calibration (factory printer — শুধু ব্যবহারকারী করতে পারেন), US patent legal check (lawyer-এর কাজ; Adobe US9741142B2 সবার আগে দেখতে হবে), DBNet swap deferred (KEEP CLASSICAL), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` পাওয়া যায়নি, ২৫টি অন্য PDF পাতা শুধু contact-sheet দেখা, page-adaptive word-gap rule (universality test-এর সবচেয়ে বড় পরের ধাপ), Raviraj p2 E-ce বাক্স y-তে overlap (descender — inpainting-এর জন্য নোট), redbox L5 'and'-এর শুধু 'a' বাঁচে ('nd'-তে কালি নেই), সাধারণ bold classification এখনো অমীমাংসিত।
- **খোলা product সিদ্ধান্ত:** ১৮টি borderless edge (faithful বনাম বন্ধ করা); integration design-এর Q-03–Q-09; DEEP-RESEARCH §১১-এর বাকি সিদ্ধান্ত।

## ৭. ফাইল

- **এই রিপোর্ট:** `improve/ROUND13-REPORT.md` (কপি: `improve/round13/merge-r13/ROUND13-REPORT.md`)
- **মার্জ ডিরেক্টরি:** `improve/round13/merge-r13/` — `segs/` (পূর্ণ বর্তমান পরিবার: ১৪ PG + r13m p2 + r13b p3), `gt/` (redbox_groups_r12, rav-p3 GT r12, n5 GT r10, r13a_gt), `pages/` (৫টি rebuild পাতা, root-এর সঙ্গে byte-identical), `cleans/` + `exemplar-pg.npy` (r12m থেকে কপি), `heading-*-300-r13m.json` (৫টি, R12-র সঙ্গে identical), `scripts/` (৪টি r13m builder, `rescore_lines_r13m.py`, `guard_check.py` + `identity_pg.json`), `verifiers/` (r11m verifier-দের কপি + `probe_identity_r13m.py` + `verify_aug2_page_r10m.py` + `check_heading_r11.py`), `clips/` (identity probe ১০টি + Aug p2 verifier ৪টি), `guard-*.json` (৬টি), `verdicts-r13m.json`, `sha-before/after.txt`, `mtime-before/after.txt`
- **Track A:** `improve/round13/track-a/` (TRACK-A-REPORT.md, seg-rav-p2-r13m.json, r13a_gt.json, verdicts-r13a.json, scripts/, clips/)
- **Track B:** `improve/round13/track-b/` (TRACK-B-REPORT.md, seg-rav-p3-r13b.json, apply_log_r13b.json, score_r13b.txt, verify_r13b.txt, verify/ overlays)
- **Track C:** `improve/round13/track-c/` (TRACK-C-REPORT.md, guard_check.py, identity_pg.json, run_guard_proof.py, proof_guard.json, guard-out-*.json, mutations/, lot_anchor_r13c.py/.json, rav_applicability_r13c.py/.json)

**ছোঁয়া হয়নি:** কোনো live পাতা (root), কোনো shared seg/verifier/builder, shared DB (শুধু read-only যাচাই), REPORT.md / REPORT-MAY.md / ROUND2–12-REPORT.md, Google Drive-এ কিছু আপলোড করা হয়নি। কোথাও OCR নেই।
