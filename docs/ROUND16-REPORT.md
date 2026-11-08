# LSE Round 16 — রিপোর্ট

**তারিখ:** ২০২৬-১১-০৭
**মার্জ ডিরেক্টরি:** `improve/round16/merge-r16/` (v8 পাতা-সেট)
**ট্র্যাক:** A — Rule D-র পরে universality পুনঃমাপা; B — SALES DEPARTMENT নিয়ম যাচাই + VALLEY hybrid (DBNet লাইন); C — CC-mask লাইভ এডিট পথে + E-ce এডিট পরীক্ষা + redbox L5 'and' + bold শ্রেণিবিন্যাস।
**নিয়ম:** কোনো কিছু Google Drive-এ আপলোড করা হয়নি; REPORT.md, REPORT-MAY.md, ROUND2–15-REPORT.md ছোঁয়া হয়নি; শেয়ার্ড Round 3 DB শুধু read-only যাচাই; কোথাও OCR নেই।

## ১. সারাংশ — হেডলাইন সংখ্যা

| বিষয় | ফল |
|---|---|
| Rule D-র universality লাভ | **মাত্র +১ শব্দ** (৯৩/১৮২ → **৯৪/১৮২**, ৫১.১% → ৫১.৬%) — SROIE base L6 "4.95"। বাকি সব অপরিবর্তিত। |
| Universality ভিত্তি-সংখ্যা সংশোধন | FUNSD base **২০/৩৮** (১৬ নয়), valley **২৭/৩৮** (২১ নয়); Tottel **১৬/২৪** (১৭ নয়); SROIE base Rule D-র পরে **৪/১৬** (৫/১৬ নয়)। মার্জ নিজে scorer পুনঃচালিয়ে নিশ্চিত করেছে। |
| SALES DEPARTMENT নিয়ম | **PROMOTE নয় — এখনো rule-search।** ১৬ পাতায় মার্জিন ধরে না (Aug −০.০৩, May −০.০৩৬, Rav p2 −০.১১+)। |
| DBNet লাইন hybrid | **সীমিত কিন্তু আসল জয়:** classical-এর মিস করা PREM GROUP (১২ শব্দ, ৬ পাতা) ধরেছে। Page-wide flag হিসেবে নির্ভরযোগ্য নয়। **KEEP CLASSICAL অপরিবর্তিত।** |
| CC-mask লাইভ পথে | **আলাদা মডিউল হিসেবে** (`inpaint_ccmask2.py`); শেয়ার্ড `inpaint.py` অপরিবর্তিত। ২-পাস ink-protected erase-এ pure-deletion ghost সমাধান (Bank's ১১৪২→১২৪ px, Nothing's ৬২৩৫→০)। Full-page CC-mask প্রমোট হয়নি। |
| E-ce y-overlap এডিট | **প্রমাণিত:** `and`→`or`, অন্য সারি ১০০% অক্ষত (BANGLADESH ink ১৭৭৩→১৭৭৩)। |
| redbox L5 'and' | **গণনাকৃত miss-ই থাকবে** — কালি শারীরিকভাবে অনুপস্থিত (০ px)। |
| Bold শ্রেণিবিন্যাস | চেষ্টা করেও **অমীমাংসিতই** (line-median সংকেত ১০/২৯)। Lot-anchor ০.০৩৬ HOLD, PG-only। |
| Raviraj p2 LINES / N5 / Description / redbox / p3 | **৩২৭/৩২৭ / ৭৭/৮১ (improved ৮১/৮১) / ৬৯/৬৯ / ৬৬/৬৬ (R9: ১৫/৬৬) / ৩৩৪/৩৮৪ (improved ৩৮৪/৩৮৪)** — সব R15-র সমান, কোনো regression নেই। |
| পূর্ণ পাতা (হর ৮৮৬) | strict ক্যানোনিক্যাল **৭৮১/৮৮৬ (৮৮.১%)**, সংশোধিত ৮৩২/৮৮৬ (৯৩.৯%), improved ক্যানোনিক্যাল ৮৩৫/৮৮৬ (৯৪.২%)। |
| লাইভ পাতা | **৫/৫ byte-identical** root-এর সঙ্গে (পুনর্নির্মাণেও) — **promotion লাগেনি**। R15-র ১-অক্ষরের diagnostic পার্থক্য এবার আসেনি। |
| পূর্ণ যাচাইসূচি | মার্জের নিজের পুনঃচালনায় সব PASS (নিচে §৬) — fontfix ৪৩/৪৩, verify_round2_300 ১৮/১৮ × ২, Guard ৫/৫, identity probe ১৫/১৫, write-back ৪১/৪১ + ৪০/৪০, save→label ৯০/৯০। |

## ২. Track A — Rule D-র পরে universality পুনঃমাপা

### ২.১ ফল: Rule D-র লাভ ঠিক এক শব্দ

| ডক / মোড | Rule D-র আগে (সংশোধিত) | Rule D-র পরে (r15c seg) | পরিবর্তন |
|---|---|---|---|
| FUNSD base | ২০/৩৮ (৫২.৬%) | **২০/৩৮** | ০ |
| FUNSD valley | ২৭/৩৮ (৭১.১%) | **২৭/৩৮** | ০ |
| SROIE base | ৩/১৬ (১৮.৮%) | **৪/১৬ (২৫.০%)** | **+১** |
| SROIE valley | ৫/১৬ (৩১.২%) | **৫/১৬** | ০ |
| Tottel | ১৬/২৪ (৬৬.৭%) | **১৬/২৪** | ০ (০ মার্জ) |
| Shields base | ১২/২৫ (৪৮.০%) | **১২/২৫** | ০ (০ মার্জ) |
| Shields valley | ১০/২৫ (৪০.০%) | **১০/২৫** | ০ (০ মার্জ) |
| **সব** | ৯৩/১৮২ (৫১.১%) | **৯৪/১৮২ (৫১.৬%)** | **+১** |

একমাত্র লাভ SROIE base L6 **"4.95"** — Rule D Op A `4`+`.`+`95` এক বাক্সে জুড়েছে। বাকি ১১টি Rule D মার্জ হয় নমুনার বাইরের লাইনে পড়েছে, নয়তো বিরামচিহ্নকে শব্দের *অংশের* সঙ্গে জুড়েছে, শব্দটি সম্পূর্ণ করেনি (১২টি মার্জের মধ্যে সম্পূর্ণ মাত্র ৫টি; যেমন "$19,750." এখনো ২ বাক্স, "1601.013:" এখনো ৫ বাক্স)। **০ false merge — পুনঃনিশ্চিত** (১২টি মার্জই wide-context crop-এ চোখে যাচাই করা)। Rule D সঠিক, কিন্তু এটি শুধু দশমিক/শেষ-বিরামচিহ্নের ভাঙন সারায় — নমুনার বেশিরভাগ miss অন্য কারণে (অক্ষর-স্তরের ভাঙন, false merge, হারানো অক্ষর, জোড়া-লাগা dot)।

### ২.২ ভিত্তি-সংখ্যার সংশোধন (ব্রিফের সংখ্যা ভুল ছিল — এবার প্রমাণসহ ঠিক করা হলো)

- **FUNSD base ১৬/৩৮ → ২০/৩৮; valley ২১/৩৮ → ২৭/৩৮।** দুটি ভুল, দুটোই পুনঃপ্রমাণিত: (ক) L12-এ Track B "the" [465,477] বলে গুনেছিল — ওই বাক্স আসলে "013" (অঙ্ক); (খ) L16-এ "agreement" exact হিসেবে বাদ পড়েছিল — পুরনো নোটে দাবি ছিল box 203 "formal-এর লেজ আর agreement-এর মাথা" ঢাকে। **মার্জ নিজে ৬× zoom চোখে দেখে নিশ্চিত করেছে:** box 203 শুধু "agreement"-ই ঢাকে, পুরোটা (formal = box 201+202)।
- **SROIE base Rule D-র পরে ৪/১৬, ৫/১৬ নয়** — ব্রিফের "৫/১৬" ছিল valley স্কোর, ভুল করে base-এ বসানো।
- **Tottel ১৭/২৪ → ১৬/২৪** — ১৭/২৪ হেডলাইন প্রতিটি per-line হিসাবের সঙ্গেই অসামঞ্জস্যপূর্ণ ছিল।
- **Shields ১২/২৫ ও ১০/২৫ নিশ্চিত**, L1/L2/L4 প্রথমবার যাচাই করা হলো (Round 15-এ হয়নি)।

### ২.৩ মার্জের নিজের যাচাই (Track A-র সংখ্যা নয়, merge-এ চালানো)

- `scorer.py` মার্জ নিজে পুনঃচালিয়েছে — আউটপুট Track A-র `scorer_out.txt`-এর সঙ্গে **অক্ষরে অক্ষরে অভিন্ন**, `PROBLEMS: none`। ১৮২টি mode-word evaluation-এর সবকটিই GT (`gt.json`) থেকে কোড-মিলিয়ে স্কোর করা।
- `diff_segs` পুনর্গঠন যাচাই: `old − merges == new seg: True` — চারটি Rule D জোড়াতেই (FUNSD base ২৮২→২৭৩, SROIE base ১২৯→১২৩, FUNSD valley ১৯৫→১৯৫, SROIE valley ১০১→৯৯)।
- সীমা (সৎভাবে): নমুনা FUNSD ৩৮, SROIE ১৬, Tottel ২৪, Shields ২৫ শব্দ — পুরো পাতার স্কোর নয়; SROIE-র আরও ২টি আসল সম্পূর্ণতা (L10 "$4.95", L12 "$0.00" আংশিক) নমুনার বাইরে বলে সংখ্যায় আসেনি; দুটি "exact" verdict coverage-সীমায় (FUNSD "7/75" ০.৮৪ — ফর্মের উল্লম্ব রুল কালি জোনে ঢুকে; SROIE "Vt" ০.৮৯ — "t"-র ২ px ডগা বাক্সের বাইরে) — দুটোই কারণসহ নির্ণয় করা, verdict বহাল। কঠোর no-exception ০.৯০ নিয়ম মানলে FUNSD base ১৯/৩৮, SROIE base ৩/১৬ হতো — কিন্তু তা ফর্মের রুল আর ২ px ডগা মাপত, segmentation নয়।

## ৩. Track B — SALES DEPARTMENT নিয়ম + VALLEY hybrid

### ৩.১ SALES নিয়ম: PROMOTE নয় — এখনো rule-search

- **পরিমাপ-কোড নিজে পুনঃচালানো হয়েছে** (Round 15-র ভুল আর হয়নি — সেবার সংখ্যা শুধু `measure6_out.txt` থেকে মেলানো হয়েছিল)। aug-p8 পুনরুৎপাদন R15-র সঙ্গে অক্ষরে অক্ষরে মিলেছে (gaps ১২৮৩; SALES|DEPARTMENT ১০px / ০.৪০; ঐ লাইনের intra সর্বোচ্চ ০.২৪)।
- **১৬ পাতায় মার্জিন ধরে না।** আর্টিফ্যাক্ট বাদ দিয়ে আসল WORD-ন্যূনতম বনাম আসল intra-সর্বোচ্চ: Aug **০.২৩ বনাম ০.২৬ (−০.০৩)**, May **০.১৯ বনাম ০.২২৬ (−০.০৩৬)**, Rav p2 **০.১৬–০.২১ বনাম ০.৩২ (−০.১১+)**, শুধু Rav p3 **+০.০৪**।
- নির্ধারক তথ্য: aug-p1-এর SALES লাইনে BY|SALES ফাঁক (৬px) ও একই লাইনের সবচেয়ে বড় intra ফাঁক (LIMITED-র M|I, ৬px) **একই পিক্সেল, একই লাইন, একই cap-height** — ফাঁকের আকার দিয়ে আলাদা করা অসম্ভব (চোখে যাচাই করা)। thr ০.২৫-এ BY+SALES **১৪টি PG পাতার ৮টিতে** ভুলভাবে মার্জ হয়ে যাবে; Aug body-তে GRAMMAGE/HEAT/NUMBER ভুলভাবে ভাঙবে (৭px, ০.২৫–০.২৬)।
- একই শব্দ-জোড়া পাতা ভেদে **±০.০৪–০.০৫** ওঠানামা করে (BY|SALES ০.২১–০.২৮) — R15-র ০.০১–০.০৩ "মার্জিন"-এর চেয়ে বড়। সেরা threshold ডকুমেন্ট-ভেদে আলাদা (PG ~০.২৩, Rav p3 ~০.৩৭)।
- ইতিবাচক দিক: সংকেত আসল — SALES|DEPARTMENT ০.৪০ সব পাতায় ধরা পড়ে; নতুন আসল over-merge পাওয়া গেছে Rav p3-তে QUANTITY|NET ০.৫৬ (এক seg বাক্সের ভেতরে লুকিয়ে)। ৮০px title লাইন পরিষ্কার (WORD-ন্যূনতম ০.৪৬–০.৪৮ বনাম intra সর্বোচ্চ ০.০৭–০.১১)।
- **পরের ধাপের প্রস্তাব (পরীক্ষিত নয়, সিদ্ধান্ত নয়):** লাইনের নিজের gap distribution থেকে adaptive threshold; অপরীক্ষিত দ্বিতীয় সংকেত — ফাঁকের দুই পাশের CC-র প্রস্থ।

### ৩.২ VALLEY hybrid — DBNet লাইন ভ্যালিডেটর: সীমিত কিন্তু আসল জয়

- **DBNet পুনঃচালনা (মার্জের ট্র্যাক নিজে চালিয়েছে):** একই মডেল (SHA `a4319856…` eval-এর pin-এর সঙ্গে মিলেছে), line সংখ্যা ৮ পাতাতেই eval-এর সঙ্গে অভিন্ন (১২৬/১২৬/১২৬/১২৩/১২৪/১২৪/১৩০/১০৭), mean best AABB IoU **১.০০০** — detection deterministic। Timing এবার ১০৯৮–১৫০৭ ms/পাতা, কিন্তু reps=2 আর VM কম ব্যস্ত ছিল — ব্যবহারকারীর i5 বা ২-সেকেন্ড bar-এর রায় নয়।
- **প্রমাণিত জয় — PREM GROUP, ১২ শব্দ:** header band-এ `PREM` + `GROUP` classical seg-এ নেই, DBNet লাইন বাক্সের ভেতরে ১০০%, **৬টি PG পাতাতেই** (Aug p1–3, May p1–3)। **মার্জ নিজে crop চোখে দেখে নিশ্চিত করেছে** (সবুজ DBNet বাক্সে PREM/GROUP পরিষ্কার) এবং `dbnet_crosscheck.json`-এ cluster ডেটা মিলিয়েছে (aug-p1: [234,174,315,200] ও [330,174,437,201], in_dbnet ১.০০)। এটাই eval-এর "safe next step"-এর কাজ।
- **সৎ negative — page-wide flag হিসেবে নির্ভরযোগ্য নয়:** Rav p2-তে ১০টি আসল শব্দ ভুলভাবে uncovered ফ্ল্যাগ পেত (decimal সারির ৮টি — DBNet লাইন ~১৫–২০px সরে গেছে, শব্দ দুই লাইনের ফাঁকে পড়েছে — plus `Consignee`, `MOHAKALI`); ১০৭টি cluster-এর মধ্যে আসল miss মাত্র ১২টি (১১%) — বাকিটা স্বাক্ষর/হাতের লেখা, halftone dot, লাল microprint, margin দাগ। Rav p2-তে ৬টি multi-row DBNet লাইন আছে (যেমন #60: ২৩ শব্দ, seg লাইন ৪১+৪২ — group করলে দুই সারি এক হয়ে যাবে, আসল ঝুঁকি)।
- **DBNet word box primary নয়; KEEP CLASSICAL অপরিবর্তিত।** প্রস্তাব (সিদ্ধান্ত নয়): DBNet লাইন শুধু **header-zone check** + মানুষের confirm-সহ "review করো" সংকেত হিসেবে; কখনো auto-add/auto-merge নয় — তার আগে signature-zone exclusion ও non-word ফিল্টার দরকার।

## ৪. Track C — CC-mask লাইভ পথে + E-ce এডিট + redbox L5 + bold

### ৪.১ CC-mask: আলাদা মডিউলই থাকবে — সিদ্ধান্ত (পরিবর্তনযোগ্য প্রস্তাব)

- নতুন মডিউল `track-c/inpaint_ccmask2.py` (R15-র `inpaint_ccmask.py` read-only import করে)। **শেয়ার্ড `inpaint.py` v4 অপরিবর্তিত** — কারণ: (ক) v4 প্রমাণিত, লাইভ পাতা byte-identical রাখতে হবে; (খ) একক-শব্দ erase পথেই CC-mask নিঃসন্দেহে ভালো; (গ) full-page পরীক্ষায় CC-mask এখনো build-time-এ নিরাপদ নয় (নিচে)।
- **R15 ysplit বাগ ধরা পড়ে ঠিক করা হয়েছে** (শুধু নতুন মডিউলে; R15 ফাইল frozen): R15-র line-median ysplit জোড়া-লাগা core-এর ওপরে পড়ত, ফলে R_other শূন্য হয়ে ১০০% ছিল vacuous। ঠিক করা হয়েছে word-box ysplit + whole-core guard দিয়ে — মেট্রিক এখন non-vacuous (R_other ০ হলে survival `None`, কখনো ১০০% নয়)।

### ৪.২ Pure-deletion ghost — এডিট পথের জন্য সমাধান

- কারণ (মাপা): হালকা-ধূসর লেবেলের <140 core পাতলা spine, চারপাশে ১৪০–১৮০ body — ১ px dilation body ঢাকতে পারে না।
- **সমাধান: ২য় পাস, ink-protected** (target বাক্সে অবশিষ্ট <210 কালি আবার মুছে, অন্য শব্দের পূর্ণ <210 কালি ১ px dilate করে রক্ষা করে):

| শব্দ | pass 1 ghost (<210 / <170 px) | pass 2 ghost | অন্য সারি |
|---|---|---|---|
| Bank's | ১১৪২ / ২০১ | **১২৪ / ০** | ১০০% |
| Nothing's | ৬২৩৫ / ৭৫৬ | **০ / ০** | ১০০% |
| Name | ৯৭৯ / ১৩৬ | **৪৭ / ১** | ১০০% |
| and (E-ce) | ৪৭৪ / ৪৯ | **৩৫ / ০** | R_other ১০০% |

- **সতর্কতা — CORE-only pass-2 protection UNSAFE, কখনো ব্যবহার করা যাবে না:** শুধু dark core (<140) রক্ষা করলে হালকা-ধূসর প্রতিবেশী কালি খেয়ে ফেলে (far −১৮ px, BANGLADESH −৫০ px)। Ink-based protection (<210) আবশ্যক। Threshold ২৩০/২৩৫ পরীক্ষা করে বাতিল (ghost আরও খারাপ: ২৭৬/৩০৩ বনাম ১২৪)।
- সৎ সীমা: ৩× zoom-এ হালকা smudge থাকে; ১×-এ প্রায় অদৃশ্য। Pass 3-এ লাভ কম (১২৪→৭১ px)।
- **Full-page CC-mask প্রমোট হয়নি:** rule exclusion grid ধ্বংস ঠিক করে (mask ৩৯৭,৬৬১→৬৯,০৫৮ px), কিন্তু CC-mask seg-মিস করা শব্দ নীরবে মুছে ফেলে (যাচাইকৃত: "68.02"-এর কোনো seg বাক্স নেই; v4 সেটা দৃশ্যমান রাখে) — নীরব data loss, দৃশ্যমান ত্রুটির চেয়ে খারাপ। Build-time promotion-এর আগে seg-completeness gate + পণ্য-সিদ্ধান্ত দরকার; rule exclusion শুধু Aug p2-তেই যাচাই করা হয়েছে।

### ৪.৩ E-ce y-overlap এডিট পরীক্ষা — প্রমাণিত

- জোড়া: L41 `and` (r15m idx310, [809,1427,873,1464]) × L42 BANGLADESH (idx316)। Erase ২-পাস ink-protected; retype `and` → `or`।
- **অন্য সারি ১০০% অক্ষত:** R_other ১৮০/১৮০, BANGLADESH exclusive ink **১৭৭৩→১৭৭৩ ঠিক একই**। **মার্জ নিজে তিন-প্যানেল crop চোখে দেখে নিশ্চিত করেছে** — ORIG-এ `and`, ERASED-এ হালকা ছায়া, EDITED-এ `or` পড়া যায়; BANGLADESH তিন প্যানেলেই অক্ষত।
- খোলা সমস্যা: caps retype (`AND`) ৬৪ px স্লটে ঢোকে না (১২২ px render হয়) — সরু স্লটে caps retype অমীমাংসিত; retype ৩×-এ আশেপাশের ছাপার চেয়ে ভারী দেখায় (DejaVu Sans Bold stand-in; পণ্যে Document DNA ব্যবহার হবে); `d`-র ascender জায়গায় হালকা ghost অবশিষ্ট।
- E-ce survey (৫টি L41 লেবেল, ঠিক করা assignment): core removal ১০০% — শুধু idx307 ৯৮.৯৮% (কারণ তদন্ত হয়নি)।
- Staging delivery (শেয়ার্ড DB-তে নয়): `lse_staging_r16c.db` — LSE-0001, STAGING-TEST, `and`→`or`; **মার্জ নিজে যাচাই করেছে: chain (True, ২, None), delivery hash ও PDF SHA রেকর্ডের সঙ্গে মিলেছে** (`a395eb80…`)।

### ৪.৪ redbox L5 'and' — গণনাকৃত miss-ই থাকবে

- বিতর্কিত strip x802–818: grey <210 = **০ px**, লাল px = **০ px** — কাগজের baseline-এর চেয়েও পরিষ্কার। L5 `and` ৪.৩ px/অক্ষর, বাকি ৬৫টি গ্রুপ ৭.৫–১৬.২ px/অক্ষর। **কালি শারীরিকভাবে অনুপস্থিত**, segmentation-এর দোষ নয় — বানালে fabrication হবে। প্রস্তাব: UI-তে এমন শব্দ "faint/partial" হিসেবে চিহ্নিত করা।

### ৪.৫ সাধারণ bold শ্রেণিবিন্যাস — চেষ্টা করেও অমীমাংসিত

- চেষ্টা করা সংকেত: line-median stroke ratio − page anchor, threshold ০.০৩৬ (Lot-anchor-এর সাধারণীকরণ)। ফল: **১০/২৯ bold লাইন** ধরা পড়ে (aug-p1 ৯/১১, aug-p2 ০/১০, may-p1 ১/২, may-p2 ০/২, may-p3 ০/৩, aug-p8 SALES ০/১)।
- কারণ (মাপা): scan type অনুযায়ী Otsu level বদলায় (colour JPEG ~১৬৬–১৭০ বনাম B&W CCITT ~১২৮–১৩৬), anchor সরে যায়; title-bar halftone H1 ratio নষ্ট করে (Aug p2 H1 পাতার সবচেয়ে নিচে); typeface/size-এর প্রভাব weight-এর চেয়ে বড়; bold/regular ব্যবধান (~০.০১–০.০২) লাইন-ভেদে তারতম্যের (~০.০৫) চেয়ে ছোট।
- **রায়: অমীমাংসিতই রইল।** Lot-anchor (একক known-regular শব্দ, PG-only, ০.০৩৬ HOLD) + heading flip-ই একমাত্র কাজের পদ্ধতি। Line-median সংকেত নতুন template-এ প্রয়োগ করা যাবে না।
- নোট: Track C-র কপি করা probe-এর প্রথম run JSON লিখেছিল merge-r15-এ (verdict অভিন্ন ১৫/১৫); `shot` পাথ merge-r15 ক্লিপে ফিরিয়ে দেওয়া হয়েছে ও কপি ঠিক করা হয়েছে — Round 15-র কোনো বিষয়বস্তু বদলায়নি।

## ৫. মার্জ — v8 পাতা-সেট (কোনো seg বদলায়নি, promotion লাগেনি)

- তিনটি ট্র্যাকের কোনোটিই প্রকাশিত seg বদলায়নি (Track A শুধু universality seg মেপেছে; Track B শুধু মেপেছে; Track C আলাদা মডিউলে কাজ করেছে) — তাই v8 সেট = r15m পরিবারই। `merge-r16/segs/` r15m-র সঙ্গে `diff -r`-এ অভিন্ন।
- r15m builder দিয়ে ৫টি লাইভ পাতা `merge-r16/pages/`-এ পুনর্নির্মাণ করা হয়েছে — **৫/৫ root-এর সঙ্গে byte-identical** (SHA: Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2 `539995a9…`, May p3 `8587be86…`)। **R15-র ১-অক্ষরের diagnostic পার্থক্য (SHORTLIST mean_iou ০.৬৪৪ বনাম ০.৬৪৩) এবার আসেনি** — এবারের rebuild root-এর সঙ্গে হুবহু মিলেছে। Heading JSON ৫টি R11-র সঙ্গে ৫/৫ identical।
- **সিদ্ধান্ত: promotion নয়।** R11-এ তৈরি root পাতাই ক্যানোনিক্যাল থাকবে।

## ৬. পূর্ণ যাচাই তালিকা (মার্জের নিজের পুনঃচালনা — ট্র্যাকের সংখ্যা নয়)

| পরীক্ষা | ফল |
|---|---|
| LINES, combined r15m (`rescore_lines_r16m.py`, merge-r16 কপিতে) | **৩২৭/৩২৭** (ok ২১৯ + correct ১০৮) |
| N5 strict / improved | **৭৭/৮১ / ৮১/৮১** (per-line R14-র সঙ্গে হুবহু) |
| Description (r10 GT) | **৬৯/৬৯, wrong ০** |
| redbox (r12 / R9) | **৬৬/৬৬ / ১৫/৬৬** |
| p3 strict / improved | **৩৩৪/৩৮৪ / ৩৮৪/৩৮৪** (SPLIT/MERGE/MISS ০/০/০, FP ১৬) |
| পূর্ণ পাতা গাণিতিক যাচাই (R12 সূত্র: ৩২৭ + ১৫ + ১০৫ = ৪৪৭; ৩২৭ + ৬৬ + ১০৫ = ৪৯৮; improved ৪৫১) | **৪৪৭/৫০২, ৪৯৮/৫০২, ৪৫১/৫০২; পূর্ণ পাতা ৭৮১/৮৮৬, ৮৩২/৮৮৬, ৮৩৫/৮৮৬** ✓ |
| PG sample | **৫১৮/৫১৮, extras ০** |
| fontfix_verify300 | **৪৩/৪৩** |
| verify_round2_300 (rebuild ধাপ RETIRED) | **১৮/১৮ × ২ বার, SHA+mtime অপরিবর্তিত** |
| repro300 | **PASS** (২টি edited span, exact text, .done, doubling নেই) |
| manual_proof300 | **১০/১০** |
| Guard check (full mode, ৫ পাতা, probe-এর আগে) | **৫/৫ PASS** (C1–C5 সব, exit ০) |
| identity probe (ফিক্সড r14m প্রোব, merge-r16 seg) | **১৫/১৫ PASS** (Lot+WIDTH+Hard × ৫; ক্লিপ মার্জ নিজে চোখে যাচাই করেছে: Aug p2 WIDTH ৭৭৬.৫ পরিষ্কার, Aug p1 Lot ২০৭/৯ পরিষ্কার, May p1 Hard অছোঁয়া, May p3 WIDTH ৭৭১.৫ পরিষ্কার) |
| write-back (R10) | **৪১/৪১ + ৪০/৪০, FAILURES: none** |
| Track D staging | **৪৮/৪৮, FAILURES: none** |
| Track C (R5) staging | **৭৪/৭৪, FAILURES: none** |
| May multipage | **৫৯/৫৯, FAILURES: none** |
| May p2/p3 (r11m verifier) | **৪৩/৪৩ PASS** |
| sqlcipher_test.py | **১৫/১৫, FAILURES: none** |
| keymgmt_proof.py | **২৫/২৫, FAILURES: none** |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** |
| Aug p2 (r10m verifier) | **১৬/১৬** (Hard neighbour untouched) |
| heading R1 (check_heading_r16m.py) | **PASS ১৪/১৪ × ৩ family** (TITLE ১৪/১৪, H2 ১৪/১৪, control-এ H1-diff ২ প্রত্যাশিত) |
| শেয়ার্ড DB (read-only) | SHA `1c065457…`, chain **(True, ২০, None)**, LSE-0001–0007, ১৪টি edit — অপরিবর্তিত |

**নোট:** Round 4-র পুরনো `verify_writeback300.py` এখনো তার ৪টি known ink-IoU fail দেখায় (৩৭ PASS) — v1 staging artifact, superseded, regression নয় (R15-র নোটের মতোই; মার্জ নিজে চালিয়ে নিশ্চিত করেছে — ৪টি fail ঠিক সেই পরিচিত IoU fail-গুলোই)।

## ৭. সৎ সীমা ও খোলা বিষয়

- **Rule D শুধু দশমিকের টুকরো সারায়** — universality-র বড় বাধা (অক্ষর-ভাঙন, false merge, হারানো অক্ষর) অপরিবর্তিত। পরের segmentation ধাপ page-adaptive word-gap (universality test-এর প্রস্তাব)।
- **SALES নিয়ম এখনো rule-search** — adaptive threshold ও CC-প্রস্থ সংকেত অপরীক্ষিত; footer-এর ২–৩টি ছোট ফাঁক "আসল না আর্টিফ্যাক্ট" অনিশ্চিত।
- **DBNet hybrid সীমিত:** PREM GROUP ধরা পড়েছে, কিন্তু page-wide flag ভুল ফ্ল্যাগ দেয়; aug-p4–8 / may-p4–6-তে DBNet চালানো হয়নি; ব্যবহারকারীর i5-এ timing মাপা হয়নি; লাল microprint দুই সিস্টেমই ধরে না (COA শব্দ নয় বলে scope-এর বাইরে)।
- **CC-mask:** full-page প্রমোট হয়নি (seg-completeness gate দরকার); rule exclusion শুধু Aug p2-তে যাচাই; title-bar/underline/grain CC-mask-এ আনা হয়নি; caps retype সরু স্লটে ঢোকে না; E-ce idx307 core removal ৯৮.৯৮% (কারণ অজানা)।
- **Bold অমীমাংসিত; redbox L5 'and' গণনাকৃত miss** (UI-তে "faint/partial" চিহ্নের প্রস্তাব)।
- **এখনো খোলা (আগের মতো):** প্রিন্ট ক্যালিব্রেশন (ফ্যাক্টরি প্রিন্টার, শুধু ব্যবহারকারী পারেন), US পেটেন্ট আইনি যাচাই (আইনজীবীর কাজ), DBNet KEEP CLASSICAL (deferred), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` পাওয়া যায়নি, ২৫টি অন্যান্য PDF পাতা শুধু contact-sheet দেখা, ১৮টি borderless edge, Q-03–Q-09।

## ৮. Round 17 প্রস্তাব

1. **Per-line adaptive word-gap threshold** — লাইনের নিজের gap distribution থেকে (Otsu/bimodal) + CC-প্রস্থ সংকেত পরীক্ষা; SALES নিয়মের পরের ধাপ।
2. **DBNet header-zone review সংকেত** — signature-zone exclusion + non-word ফিল্টার সহ, মানুষের confirm-সহ; auto-add/merge কখনো নয় (পণ্য-সিদ্ধান্ত দরকার)।
3. **Full-page CC-mask-এর gate** — seg-completeness যাচাই + rule exclusion সব ৫টি PG পাতা + May-তে যাচাই, তারপর build-time promotion বিবেচনা।
4. **Caps retype সরু স্লটে** — ৬৪ px স্লটে `AND`-ধরনের caps কীভাবে বসবে (font condens / অক্ষর-সংকোচন / স্লট-সম্প্রসারণ — কোনোটাই সিদ্ধান্ত নয়)।
5. **E-ce idx307 core removal ৯৮.৯৮%** — কারণ তদন্ত।
6. **Bold-এর নতুন সংকেতের ধারণা** — line-median ratio ব্যর্থ; অন্য principled সংকেত খোঁজা।
7. **Universality নমুনা-বিস্তার** — Rule D-র বাইরে page-adaptive word-gap-এর প্রথম পরীক্ষা (FUNSD/SROIE/Tottel/Shields একই নমুনায়)।
8. **Q-03–Q-09** — এখনো খোলা পণ্য-সিদ্ধান্ত।

## ৯. ফাইল তালিকা

- **প্রতিবেদন:** `improve/ROUND16-REPORT.md` (+ কপি `improve/round16/merge-r16/ROUND16-REPORT.md`)
- **মার্জ ডিরেক্টরি:** `improve/round16/merge-r16/` — `segs/` (১৭টি, r15m-র সঙ্গে অভিন্ন), `scripts/` (৪টি r16m builder + `guard_check.py` + `identity_pg.json` + `rescore_lines_r16m.py` + N5/Description/redbox/p3 scorer + `sample_rows_r16m.py`), `verifiers/` (probe_identity_r14m + may23/aug2/heading-এর r16m কপি), `pages/` (৫টি rebuild পাতা — root-এর সঙ্গে ৫/৫ byte-identical), `clips/` (১৫টি identity ক্লিপ + ১৪টি sample-rows crop), `cleans/` (r15m থেকে কপি), `exemplar-pg.npy`, `heading-*-300-r11m.json` (৫টি, R11-র সঙ্গে identical), `verdicts-r15m.json`, `verify-logs/` (২৫টি), `probe_identity_r14m.json`, `verify-may23-summary-r16m.json`
- **Track A:** `improve/round16/track-a/` (RESULTS.md, gt.json — ১৮২ evaluation, scorer.py + scorer_out.txt, diff_segs.py, strips/ ১৪৭ ফাইল, merges/ ২৪ crop, rule_d_copy.py)
- **Track B:** `improve/round16/track-b/` (RESULTS.md, measure_sales_all.py + measure_sales_segline.py, gaps-*.json ×৩২, dbnet-r16-*.json ×৮, dbnet_crosscheck.py + dbnet_crosscheck.json, crops/ — SALES + DBNet চোখে-যাচাই)
- **Track C:** `improve/round16/track-c/` (RESULTS.md, inpaint_ccmask2.py, retype_and.py, staging_delivery.py, bold_signal.py, probe_redbox_and*.py, diag_ghost*.py, guard/ ৫টি, clips/ ১৫টি, crops/ চোখে-যাচাই, inpaint/ — CC-mask erase + E-ce এডিট, staging/ — lse_staging_r16c.db + lse-r16c-and-or.pdf)
- **কিছুই Google Drive-এ আপলোড করা হয়নি।** শেয়ার্ড Round 3 DB শুধু read-only যাচাই করা হয়েছে; নতুন delivery staging DB-তেই আছে।
