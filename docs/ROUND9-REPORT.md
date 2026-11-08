# LSE — Round 9 রিপোর্ট

**তারিখ:** ২০২৬-১১-০৭ | **কোঅর্ডিনেটর:** Round 9 merge (একমাত্র কোঅর্ডিনেটর; কোনো scheduled job নয়, কোনো দ্বিতীয় কোঅর্ডিনেটর নয়)
**আগের রাউন্ড:** Round 8 সম্পূর্ণ (ROUND8-REPORT.md, SHA 40906758d98d6885…)

## ১. সারাংশ — মূল সংখ্যা

| বিষয় | Round 8 | **Round 9 (merge-এর নিজের re-run)** |
|---|---|---|
| Description (Raviraj p2) | ৩৮/৬৯ | **৬৯/৬৯** (সংশোধিত GT-তে; R8 GT-তে ৬১/৬৯; NOT সহ ৭০/৭০) |
| Aug-p2 e-mail tail | miss (৩ টুকরো) | **ঠিক** — ১ বাক্স [971,415,1271,445], IoU_m ০.৭০৫৫ |
| N5 (Raviraj পূর্ণ-পাতা) | ২৬ বনাম ৩১ (অমীমাংসিত) | **মীমাংসিত: r8m-এ ৩৮/৮১ (কঠোর), r9m-এ ৫৭/৮১** |
| Raviraj পূর্ণ-পাতা গোনা | ৩৪৬/৩৯৪ = ৮৭.৮% (১০১-শব্দের নমুনা, পূর্ণ পাতা নয়) | **৫৬০/৭৯৫ = ৭০.৪% (প্রথম সত্যিকারের পূর্ণ-পাতা গোনা)** |
| May p2/p3 (bold knife-edge) | ৪২/৪৩ | **৪২/৪৩** — একই fail, কোনো নীতিগত সমাধান পাওয়া যায়নি |
| Live পাতা | ৫টি (Aug p2 aced12fc…) | **৫টি — ৪টি byte-identical, Aug p2 নতুন (3dbab180…)** |
| fontfix_verify300 | ৪৩/৪৩ | **৪৩/৪৩** |
| Identity probe (৫ পাতা) | ১৫/১৫ | **১৫/১৫** (চোখে দেখা) |
| শেয়ার্ড DB | SHA 1c065457…, ২০ entry | **অপরিবর্তিত — SHA 1c065457…, ৭ delivery, ২০ audit entry** |

**এক লাইনে:** Description সম্পূর্ণ (৬৯/৬৯), e-mail tail ঠিক, N5 মীমাংসিত, Raviraj-এর প্রথম সত্যিকারের পূর্ণ-পাতা গোনা ৭০.৪%। Bold knife-edge ঠিক হয়নি — তবে এবার প্রমাণসহ প্রমাণিত যে কোনো signal-ই কাজ করে না। Merge-এ একটি আসল regression ধরা পড়েছে (H1/bar_ink) এবং ঠিক করা হয়েছে — নিচে §৫ দেখুন।

## ২. Track A — Description-এর বাকি ৩১ শব্দ + Aug-p2 e-mail tail

**ফল: Description ৩৮/৬৯ → ৬৯/৬৯ (সংশোধিত GT-তে), ০ false merge।**

- **Matcher-এর ৪টি নেতিবাচক ফল (প্রমাণসহ):** white-run gate কাজ করে না (ভেতরের ১–৮ বনাম মাঝের ০–৯, পুরো মিশে আছে); DNA font Description-এর কালির সঙ্গে মেলে না (IoU ০.১৩–০.৪১, ~৩০% সরু); letter-ID ভাঙা (top-1 ২২.৭%); whole-word IoU আলাদা করে না (একই শব্দ ০.২৭১–০.৭৯৬ বনাম ভিন্ন শব্দ ০.৩১৮–০.৬৫০)। বাক্স বসানো হয়েছে component + profile-neck + চোখে দেখে; matcher শুধু সহায়ক প্রমাণ।
- **৯টি GT span সংশোধিত** (প্রতিটির component + চোখের প্রমাণ আছে): L10 VALUE [634,715], USD [736,786]; L12 number [913,1092]; L13 ISSUING [558,652], BANK'S [662,749], BIN [758,796], REGN. [806,878], NO. [881,914], number [923,1100]। R8-এর GT ফাইল অপরিবর্তিত রাখা হয়েছে।
- **সৎ ধরা (Track A-র নিজের ভুল, নিজেই ধরেছে):** প্রথম L13 fix ভুল ছিল — REGN. [805,915] NO.-কে গিলে ফেলেছিল; NO. [916,974] আসলে number-এর প্রথম ৪ digit "0004" ছিল; number [974,1102] তার প্রথম ৪ digit হারিয়েছিল। ৬× zoom-এ চোখে দেখে ধরা পড়েছে। Scorer তখনো ৬৯/৬৯ দেখিয়েছিল কারণ GT আর seg একই ভুল থেকে বানানো হয়েছিল (circular) — দুটোই ঠিক করা হয়েছে। **শিক্ষা:** scorer-এর সংখ্যা একা যথেষ্ট নয়; GT-ও চোখে যাচাই করতে হয়।
- **Aug-p2 e-mail tail ঠিক:** ৩০১ → ২৯৯ শব্দ; পুরো e-mail এক বাক্সে [971,415,1271,445], IoU_m ০.৭০৫৫, margin ০.২৬৯, চোখে যাচাই করা।
- **খোলা:** QUANTITY-র ভেতরের letter-split অমীমাংসিত; www.pgfoils.in অমীমাংসিত (১৪ পাতায় কোথাও exemplar নেই); সংশোধিত GT কোঅর্ডিনেটরের অনুমোদন পেয়েছে (নিচে §৫)।
- **ফাইল:** `improve/round9/track-a/track-a-report.md`, `segs/seg-rav-p2-r9.json` (৬০০ শব্দ), `segs/seg-aug-p2-r9.json` (২৯৯ শব্দ), `data/desc-ground-truth-r9.json`।

## ৩. Track B — bold-rule robustness (knife-edge)

**ফল: ঠিক হয়নি — কোনো signal কাজ করে না, আগের চেয়ে শক্ত প্রমাণসহ।**

- **Knife-edge এখন ৩ পাতায়, ১টিতে নয়:** May-p1 WIDTH margin −০.০০০১৩৮, Aug p2 −০.০০১০৩৪, May-p3 +০.০০০৬৫১। কোনো পাতায় gap নেই (−০.০১৩৬…−০.০৩২২)।
- **Round 8-এর gap signal ছিল probe-selection artefact:** MAIN-30 gap +০.০২৬ অক্ষত, কিন্তু ১০টি observation-column শব্দ যোগ করলে gap −০.০৩৫ হয়ে যায়; leave-one-page-out: কোনো fold-এই train-এ gap নেই — threshold fit করা যায় না।
- **অন্য candidate-রাও fail:** (d) 1px erosion FAIL (Aug p2 আর May-p1 WIDTH-কে bold বানিয়ে দেয়); (e2) same-line median bold recall ভাঙে (৪–৭/১০–১৮); (e3) same-size-band May bold recall ২–৫/১০; (e1) obs-column median circular (column-এ সংজ্ঞা অনুযায়ী শুধু regular value থাকে); document/pooled median FAIL (Aug pooled Aug-p2 WIDTH-কে bold বানায়)।
- **R7 §৭-এর ধারণা মূল্যায়ন:** (c) ০.৯৮ margin আসল সমস্যা নয় (R8 §৮ সমর্থন করে: fontfix-এ width-সংক্রান্ত কোনো fail নেই)।
- **সিদ্ধান্ত-সহায়ক মাপ:** May WIDTH-এর expectation bold-এ বদলালে fit-এর খরচ প্রায় শূন্য — DNA bold advance regular-এর চেয়ে মাত্র +০.১–০.৫% বেশি (font-size ০.৯৯৫–০.৯৯৯×)। Track B বদলায়নি — এটি parent/user-এর সিদ্ধান্ত (৩টি May পাতা আবার build করতে হবে + verifier expectation বদলাতে হবে)। না বদলালে ৪২/৪৩-ই documented exception হিসেবে থাকবে।
- **নিয়ন্ত্রণ দুবার চালানো:** fontfix_verify300 ৪৩/৪৩, May p2/p3 ৪২/৪৩ (একমাত্র fail অপরিবর্তিত: May-p3 WIDTH obs regular)। কোনো ফাইল বদলায়নি, কোনো OCR ব্যবহার হয়নি।
- **ফাইল:** `improve/round9/track-b/track-b-report.md`, `track-b/scripts/`।

## ৪. Track C — N5 ২৬ বনাম ৩১ + Raviraj পূর্ণ-পাতা গোনা

**ফল: N5 মীমাংসিত; Raviraj-এর প্রথম সত্যিকারের পূর্ণ-পাতা গোনা সম্পূর্ণ।**

### ৪.১ N5 — মীমাংসিত সংখ্যা ৩৮/৮১ (কঠোর, বর্তমান r8m seg-এ)
- **Denominator ৮১-এ স্থির হয়েছে** (৭৭ শব্দ + ৪টি colon token, ৮২ নয়; R6-এর নিজের অংশগুলোর যোগফল ৭২, ৮২ নয়)। ৮২ দেয় এমন কোনো সামঞ্জস্যপূর্ণ নিয়ম নেই।
- **R6-এর ৩১ ≈ loose eye-count** (স্পষ্ট loose নিয়মে ৩৩/৮১; R6-এর চোখে ৩১ — একই নিয়ম-পরিবার, ~২ শব্দের চোখের পার্থক্য + denominator ৮২ বনাম ৮১)।
- **R7-এর ২৬ = একই seg-এ loose-পরিবারের পুনর্গোনা**, সঙ্গে render-label ভুল-পড়া (R7-এর নিজের স্বীকৃত ভুলের ধরন)।
- **R7-এর ≤২৩ "সংশোধন" ভুল** — cluster seg-এ SB বাক্স (557,2036,588,2053) আর NO বাক্স (597,2036,630,2053) স্পষ্টভাবে আছে; "কোনো বাক্স নেই" শুধু r6base seg-এর ক্ষেত্রে সত্য (০/৮১)।
- **নতুন স্বাধীন GT:** `gt/n5-ground-truth-r9.json` (চোখ + CC মাপ, OCR নয়); scorer `scripts/n5_score.py` (কঠোর) ও `n5_score_loose.py`।
- **r9 seg-এ N5 ৫৭/৮১** (Description ৪২/৪২) — সংশোধিত GT-তে merge-এর re-run (§৫)।
- গোনার সময় সংশোধন (box-data overlay-পড়াকে হারিয়েছে): E-consignor ১৩→৯/১৯, E-consignee ১৫→১২/৪৯, Invoice ৫→৭/১০, G-consnote INDIA miss নয়, split; N3 Actual+Charged দুটোই ০।

### ৪.২ Raviraj পূর্ণ-পাতা গোনা — r8m ৫২৯/৭৯৫ = ৬৬.৫%, r9m ৫৬০/৭৯৫ = ৭০.৪%
- **নতুন ৫০২-শব্দের p2 GT** (`gt/p2-wordlists-r9.py`, ১৫টি non-overlapping region, প্রতিটি শব্দ একবার) + p3 R5 থেকে যাচাই করা (seg R5 থেকে অপরিবর্তিত)।
- **r8m: ৫২৯/৭৯৫ = ৬৬.৫%** (p2 ২৭৩/৫০২ = ৫৪.৪%, p3 ২৫৬/২৯৩ = ৮৭.৪%); R6 cluster ৪৮৪/৭৯৫ (৬০.৯%), r7 ৫০৮/৭৯৫ (৬৩.৯%)।
- **সতর্কতা:** R7-এর ৮৭.৮% (৩৪৬/৩৯৪) ছিল ১০১-শব্দের region নমুনা + p3, পূর্ণ পাতা নয় — ৭৯৫-শব্দের denominator-এর সঙ্গে সরাসরি তুলনা চলে না। ৬৬.৫% → ৭০.৪% উন্নতি, ৮৭.৮% থেকে "পতন" নয়।
- **কোনো fix attempt করা হয়নি, কোনো seg promote করা হয়নি** — কোনো fix-ই প্রমাণের মানদণ্ড (০ false merge + কোনো regression নয়) পূরণ করেনি।
- **Round 10-এর #১ candidate (মাপাসহ):** decimal-point split (p2: 10138.43KGS, 58802.89, 10138.43; p3: R2/R3-তে ৯টি) — seg-algorithm বদল + পূর্ণ regression লাগবে।
- **খোলা:** `raviraj COA 20 micron.jpg` workspace-এ কোথাও পাওয়া যায়নি — গোনা হয়নি, আবার download করা হয়নি; PDF-এর বাকি ২৫ পাতা শুধু contact sheet-এ দেখা হয়েছে, হাতে গোনা হয়নি (~৮০০০ শব্দ — এক session-এ সম্ভব নয়); p3-র R2/R3 GT line-list R5 থেকে উদ্ধার করা যায়নি (শুধু count + failure-list আছে)।
- **ফাইল:** `improve/round9/track-c/track-c-report.md`, `gt/n5-ground-truth-r9.json`, `gt/p2-wordlists-r9.py`, `scripts/`।

## ৫. Merge — r9m পরিবার, H1 regression ধরা ও ঠিক করা, পাতার SHA

Merge ডিরেক্টরি: `improve/round9/merge-1089/` (নিজের ডিরেক্টরি; অন্য agent-এর সঙ্গে কোনো সংঘর্ষ নেই)।

### ৫.১ Track A যাচাই (কোঅর্ডিনেটরের নিজের re-run)
- `desc_score_r9.py` আবার চালানো: **r9 seg + সংশোধিত GT ৬৯/৬৯, wrong ০**; r9 seg + R8 GT ৬১/৬৯ (ভুল ৮টি: L10 VALUE/USD + L13 ISSUING/BANK'S/BIN/REGN./NO./number); r8m seg + সংশোধিত GT ৪০/৬৯।
- L13 tail ৬× clip চোখে দেখা (REGN./NO./000443918-0101 বাক্স সঠিক) এবং aug-p2-email-final clip (pgfoils@pgfoils.in-এর ওপর ঠিক এক বাক্স)। **সংশোধিত GT অনুমোদিত।**
- **Seg diff যাচাই:** rav-p2 r8m ৫৯৭ → r9 ৬০০ শব্দ; ২৮টি সরানো, ৩১টি যোগ — সব Description region-এর ভেতরে (বাইরে একটিও নয়)। aug-p2 ঠিক e-mail merge: ৩ বাক্স সরানো ([971,416,1061,445], [1122,415,1212,445], [1246,424,1271,441]), ১টি যোগ ([971,415,1271,445]); ৩০১→২৯৯।
- **N5 সমন্বয়:** Track C-র N5 GT-তে তখনো পুরোনো (ভুল) L10/L13 span ছিল, তাই r9 seg-এ ৪৯/৮১ কম গুনেছিল। কোঅর্ডিনেটর সংশোধিত N5 GT বানিয়েছে (`merge-1089/n5-ground-truth-r9m.json`, L10/L13 span সংশোধিত desc GT থেকে নেওয়া, component + ৬× চোখে যাচাই) এবং scorer আবার চালিয়েছে: **N5 r9 seg-এ ৫৭/৮১ (Description ৪২/৪২)**, r8m control-এ ৪০/৮১। Scorer-এর "৬৯/৬৯" NOT শব্দটিকে নিয়ম অনুযায়ী বাদ দেয় (`if word=="NOT": continue`, denominator hardcode ৬৯); NOT বাক্স r9 seg-এ যাচাই করা হয়েছে (550,1737,599,1754) — অর্থাৎ **Description NOT-সহ ৭০/৭০**।
- **সমন্বিত Raviraj p2 মোট (r9 seg): ৩০৪/৫০২ = ৬০.৬%** (২৭৩ − ৩৯ + ৭০; ৩৯ ছিল Track C-র r8m-এ Description উপাদান, ৭০ সংশোধিত Description গোনা)। **পূর্ণ-পাতা ৫৬০/৭৯৫ = ৭০.৪%** (r8m-এ ৫২৯/৭৯৫ = ৬৬.৫% ছিল)।

### ৫.২ Seg line=None সমস্যা (merge-এ ধরা, ঠিক করা)
- r9 aug-p2 seg-এ merged e-mail বাক্সের `line: None` ছিল — এতে builder-এর heading detection ভেঙে গিয়েছিল (`sorted()`-এ TypeError)। **ঠিক করা:** e-mail বাক্সের line = ৩ (প্রতিবেশী সব বাক্স line ৩)।
- r9 rav-p2 seg-এ ৮০টি শব্দের line=None — কিন্তু r8m seg-এও ৭৭টি শব্দের line=None (Description region-এর শব্দগুলোর কোনো seg-পরিবারেই line assignment নেই)। Overlap-এ line নকল করার চেষ্টা ব্যর্থ হয়েছে (r8m-এও None) — **তাই r9 rav-p2 seg ঠিক Track A-র দেওয়া অবস্থায় promote করা হয়েছে**, line বানানো হয়নি। এটি scoring-only seg (Raviraj p2-র কোনো live পাতা নেই) এবং কোনো scorer seg-এর line ব্যবহার করে না — ক্ষতিকর নয়, তবে seg-format-এর একটি জানা ফাঁক হিসেবে লিপিবদ্ধ রইল।
- **r9m পরিবার** (`merge-1089/segs/`, ১৫টি): aug-p2 + rav-p2 r9, বাকি ১৩টি r8m-এর byte-identical কপি (r9m নামে)।

### ৫.৩ H1 regression — merge-এ ধরা, মাপা, ঠিক করা
e-mail merge-এর একটি অপ্রত্যাশিত পার্শ্ব-প্রতিক্রিয়া ধরা পড়েছে:
- **সমস্যা:** merged e-mail বাক্স [971,415,1271,445] bar-এর dither-করা gap-গুলো ঢেকে ফেলায় line 3-এর `bar_ink` ০.১৭৬ (r7m) → ০.১২৫ (r9m) হয়ে ০.১৫ threshold-এর নিচে নেমে যায়; line 3 H1 থেকে বাদ পড়ে। ফলে দুটি line-3 শব্দ regular হয়ে গিয়েছিল: [1564,414,1676,450] ("www.pgfoils.in"-এর লেজ, ratio ০.১১৪) এবং merged e-mail বাক্সটি নিজে (ratio ০.১২১) — অথচ মূল scan-এ পুরো header line-টি bold।
- **প্রমাণ বার আসল:** line-3 band-এর গড় grey ১৭৫.৭ বনাম কাগজ ২৪৯.৩; চোখে দেখা — header-এর লেখা bold।
- **Threshold কমানো যায়নি:** ১৪ PG পাতায় H1-এর bar_ink সর্বনিম্ন ০.১৫৩, non-H1 সর্বোচ্চ ০.১৪৩ (gap মাত্র ০.০১০); r9m line 3 (০.১২৫) অন্যান্য পাতার non-H1 header line-গুলোর (০.১১৬–০.১৪৩) মাঝখানে পড়ে — কোনো পরিষ্কার gap নেই। (আরো দেখা গেছে: header line সব পাতাতেই knife-edge-এ আছে — শুধু Aug-p2 r7m-ই ০.১৫ পার হয়েছিল।)
- **ঠিক করা (documented override):** Aug-p2 builder-এ line 3-কে H1-এ জোর করে যোগ করা হয়েছে, মাপ ও কারণসহ মন্তব্য লিখে (`build_page_aug2_300_r9.py`)। **যাচাই:** common বাক্সগুলোতে bold-এর পার্থক্য **০টি** (R8 বনাম R9); bold count ৭১ → ৬৯ — পার্থক্য শুধু e-mail merge-এর (৩টি bold টুকরো → ১টি bold বাক্স)। Merged e-mail বাক্স এখন bold (fontWeight ৭০০, DOM-এ যাচাই) এবং চোখে দেখা — header line পুরোটা bold।
- **সঠিক সমাধান Round 10-এ:** heading detection-কে merge-robust করা (gap-ink/bar_ink combination, ১৪ পাতায় যাচাই করে) — merge phase-এ algorithm বদলানো হয়নি।
- **Clean background আবার বানানো হয়েছে** r9 seg দিয়ে: inpaint ২৯৯ বাক্স / ৮০১,৭০৫ masked px (R8: ৩০১ / ৭৯৯,০৪৬ — পার্থক্য merged বাক্সের gap-গুলো); manual clean sig বাক্স ৮২৮০→০, ৪৮৪৩→০, frame rule ১৩৬২/১৩৬২ অক্ষত।

### ৫.৪ পাতা rebuild ও SHA
- **৪টি অপরিবর্তিত পাতা byte-identical rebuild হয়েছে** (backup-এর সঙ্গে SHA মিলেছে): Aug 047a6d6b…, May 8944d835…, May p2 82ab16d0…, May p3 db72deaa…।
- **Aug p2 নতুন পাতা:** SHA **3dbab18066d913ab…** (আগে aced12fc…) — ২৯৯ শব্দ, ৬৯ bold শব্দ, ৩ heading flip। Root-এ promote করা হয়েছে; heading JSON-ও আপডেট করা হয়েছে (h1_lines [3, 5], R8-এর মতো)।
- Backup: merge-আগের ৫টি পাতা + root seg `merge-1089/backup/`-এ, SHA যাচাই করা।

## ৬. চূড়ান্ত যাচাই টেবিল (merge-এর নিজের re-run — সব সংখ্যা এই রাউন্ডে চালিয়ে মাপা)

| যাচাই | ফল (Round 9 merge) | Round 8 |
|---|---|---|
| fontfix_verify300 | **৪৩/৪৩** | 43/43 |
| verify_round2_300 | **১৮/১৮** | 18/18 |
| repro300 (doubling) | **PASS** | PASS |
| manual_proof300 | **১০/১০** | 10/10 |
| Identity probe (Lot+WIDTH+Hard, ৫টি live পাতা) | **১৫/১৫** (চোখে দেখা — Lot পরিষ্কার, WIDTH পরিষ্কার, "Hard" অক্ষত, doubling নেই) | 15/15 |
| Write-back (merge, canonical) | **৪১/৪১, FAILURES: none** | 41/41 |
| Write-back (track-a, Round 3-এর পুরোনো staging) | **৩৭/৪১** — ৪ ink-IoU fail (§৭ দেখুন; Round 9-এর regression নয়) | (আলাদা করে রিপোর্ট হয়নি) |
| Track D staging | **৪৮/৪৮** | 48/48 |
| Track C staging | **৭৪/৭৪** | 74/74 |
| May multipage | **৫৯/৫৯** | 59/59 |
| May p2/p3 | **৪২/৪৩** — ১ fail: May-p3 WIDTH obs regular (weight=700), knife-edge (§৩) | 42/43 |
| sqlcipher | **১৫/১৫** | 15/15 |
| keymgmt | **২৫/২৫** | 25/25 |
| Save→label live (৫ পাতা) | **৯০/৯০** | 90/90 |
| Aug p2 live পাতা (r8c) | **১৬/১৬** | 16/16 |
| PG sample (r9m seg) | **৫১৮/৫১৮, অতিরিক্ত ০**; টাইটেল ১৪/১৪, H2 ১৪/১৪ | 518/518 |
| Description (r9m seg, সংশোধিত GT) | **৬৯/৬৯** (NOT-সহ ৭০/৭০) | 38/69 |
| N5 (r9m seg, সংশোধিত GT) | **৫৭/৮১** (Description ৪২/৪২); r8m-এ কঠোর ৩৮/৮১ | 26 বনাম 31 (অমীমাংসিত) |
| Raviraj পূর্ণ-পাতা (r9m) | **৫৬০/৭৯৫ = ৭০.৪%** (p2 ৩০৪/৫০২ = ৬০.৬%, p3 ২৫৬/২৯৩ = ৮৭.৪%) | 346/394 = 87.8% (নমুনা, পূর্ণ পাতা নয়) |
| শেয়ার্ড DB (read-only যাচাই) | **SHA 1c065457…, ৭ delivery, ২০ audit entry — অপরিবর্তিত** | একই |

**নোট:** fontfix/verify_round2/repro/manual/identity/save→label/Aug-p2 — চূড়ান্ত shared-tree অবস্থায় (নতুন Aug p2 পাতাসহ) আবার চালানো হয়েছে। Write-back/Track D/Track C/multipage/sqlcipher/keymgmt — staging DB/ফাইলে চলে। Description/N5 — চূড়ান্ত r9m seg + সংশোধিত GT-তে আবার চালানো হয়েছে।

## ৭. সৎ সীমা — এখনো যা সম্পূর্ণ নয়

- **May-p3 WIDTH knife-edge (৪২/৪৩):** Track B প্রমাণ করেছে কোনো principled signal নেই। May WIDTH-এর expectation bold-এ বদলানো (fit-খরচ ~০) parent/user-এর সিদ্ধান্ত — §৮ দেখুন।
- **Write-back track-a ৩৭/৪১ (Round 9-এর regression নয়):** Round 3-এর track-a staging PDF-গুলো পুরোনো font/size-এ বানানো; verifier-এর fresh reference render বর্তমান font/size ব্যবহার করে — ৪টি ink-IoU ০.৩১–০.৪১ (threshold ০.৯০)। সম্ভাব্য কারণ: Round 4-এর full-precision font-size fix (Lot IoU ০.৫১৯ → ১.০০০) track-a artifact-এ নেই। Canonical merge version ৪১/৪১ PASS — এটাই R8-এর সংখ্যা। Track-a staging-টি Round 4-এ supersede হয়েছে; আলাদা করে rebuild করা হয়নি।
- **Raviraj ৭০.৪%:** decimal-point split-গুলো ঠিক হয়নি (Round 10-এর #১ candidate)। QUANTITY-র ভেতরের letter-split, www.pgfoils.in অমীমাংসিত। N5 ৫৭/৮১।
- **H1 detection merge-robust নয়:** line-3 override দিয়ে ঠিক করা হয়েছে (§৫.৩), কিন্তু algorithm-এর আসল fix Round 10-এ বাকি।
- **এখনো খোলা (আগের রাউন্ড থেকে):** print calibration (factory printer লাগবে); US patent আইনি যাচাই (উকিলের কাজ); DBNet swap deferred; DPAPI প্রমাণ হয়নি VM-এ; Aug-p2 e-mail-এর আগের ভুল fix-এর শিক্ষা — GT-ও চোখে যাচাই করতে হয়।

## ৮. সিদ্ধান্তের জন্য (parent/user)

1. **May WIDTH expectation bold-এ বদলাবো কি?** (Track B) — fit-খরচ প্রায় শূন্য (DNA bold advance +০.১–০.৫%)। বদলালে: ৩টি May পাতা rebuild + verifier expectation বদল + পূর্ণ re-run। না বদলালে: ৪২/৪৩ documented exception হিসেবে থাকবে। Track B বদলায়নি — সিদ্ধান্ত আপনাদের।
2. **Round 10 শুরু করবো কি?** প্রার্থী (§৯) — decimal-point split fix-ই সবচেয়ে বড় একক লাভ (Raviraj p2/p3-তে ~১২টি split)।

## ৯. Round 10-এর প্রার্থী (মাপাসহ)

1. **Decimal-point split** — Raviraj p2/p3-তে ~১২টি (10138.43KGS, 58802.89, 10138.43 + p3-তে ৯টি)। Seg-algorithm বদল + পূর্ণ regression লাগবে।
2. **H1 detection merge-robust করা** — gap-ink/bar_ink combination, ১৪ PG পাতায় যাচাই (§৫.৩-এর override সরানো)।
3. **Description QUANTITY inner letter-split + www.pgfoils.in** — exemplar নেই; নতুন ধারণা লাগবে।
4. **N5 ৫৭/৮১ → উপরে** — বাকি miss-গুলোর ধরন ধরে fix।
5. **Write-back track-a staging rebuild** — Round 3 artifact-কে বর্তমান font/size-এ আবার বানানো (৩৭/৪১ → ৪১/৪১)।

## ১০. ফাইল ও SHA

- **এই রিপোর্ট:** `improve/ROUND9-REPORT.md`
- **Track রিপোর্ট:** `improve/round9/track-a/track-a-report.md`, `improve/round9/track-b/track-b-report.md`, `improve/round9/track-c/track-c-report.md`
- **Merge ডিরেক্টরি:** `improve/round9/merge-1089/` — `segs/` (r9m পরিবার, ১৫টি), `pages/live-scan-page-aug-p2-300.html`, `backup/` (merge-আগের ৫ পাতা), `n5-ground-truth-r9m.json`, `probe_identity_r9m.py`, `sample_rows_r9m.py`, `check_titles_h2_r9m.py`, `build_page_aug2_300_r9.py`, `manual_clean_aug2_r9.py`, `clips/` (r9m-aug2-lot/width/email/website-tail — চোখে যাচাই করা)
- **Live পাতা (বর্তমান):** Aug 047a6d6b…, **Aug p2 3dbab180… (নতুন)**, May 8944d835…, May p2 82ab16d0…, May p3 db72deaa…
- **শেয়ার্ড DB:** SHA 1c065457…, ৭ delivery (LSE-0001–0007), ২০ audit entry, hash chain intact — read-only যাচাই, কোনো লেখা হয়নি।
- **Drive-এ আপলোড করা হয়নি** (নিয়ম অনুযায়ী); REPORT.md, REPORT-MAY.md, ROUND2–8-REPORT.md অপরিবর্তিত।
