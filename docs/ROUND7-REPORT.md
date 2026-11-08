# LSE — Round 7 রিপোর্ট (Live-Scan Editing)

**তারিখ:** ২০২৬-১১-০৬ · **স্থিতি: সম্পূর্ণ — তিন ট্র্যাক এক v8 পাতা সেটে merge করা, পুরো suite নিজে আবার চালিয়ে যাচাই করা।**

> **প্রসঙ্গ:** ব্যবহারকারী ঘুমানোর আগে (২০২৬-১১-০৬ ~২৩:০৬) LSE-র জন্য **blanket permission** দিয়েছেন — তার অনুমতির অপেক্ষায় সময় নষ্ট না করে নিজের বিচারে কাজ চালিয়ে যেতে হবে, খোলা প্রশ্ন নিজেই সিদ্ধান্ত নিতে হবে; তিনি যেকোনো সিদ্ধান্ত পরে বদলাতে পারেন। এই রাউন্ডের দুটি সিদ্ধান্ত (OCR-tiebreaker, নিচে §২) সেই অনুমতির অধীনে নেওয়া। শারীরিকভাবে তার ছাড়া অসম্ভব দুটি কাজ আগের মতোই খোলা: print calibration (ফ্যাক্টরির প্রিন্টার), US পেটেন্টের আইনি যাচাই (উকিল)।

## ১. এক লাইনে ফল

- **Track A — per-page লেবেল (b1 + c3):** ৫টি লেবেল, প্রতিটি নিজের পাতার Lot+WIDTH; migration v1→v2→v3 প্রমাণিত (২৯/২৯), ইতিহাস অক্ষত; যাচাই **১৪৬/১৪৬**।
- **Track B — ttfautohint: DO NOT PROMOTE** (সৎ নেতিবাচক ফল)। Hinting WIDTH match খারাপ করে (Aug +0.111 → +0.048, May +0.088 → +0.060); ০.৯৮-র ২% margin এখনো খোলা।
- **Track C — vocabulary gate + Raviraj:** নমুনা **৫১৮/৫১৮, অতিরিক্ত ০** (৪ speck FP শেষ); Raviraj **৮৬.০% → ৮৭.৮%** (৩৪৬/৩৯৪); Description মেগা-বাক্স ৩ → ০।
- **Merge:** OCR-মুক্ত অংশ promote করা হয়েছে (S1, Z2, লাল-কালি); **৬টি OCR-সিদ্ধান্ত merge promote করা হয়নি** — সিদ্ধান্ত §২-এ। চূড়ান্ত যাচাই §৭-এ: fontfix **৪৩/৪৩**, verify_round2_300 **১৮/১৮**, write-back **৪১/৪১**, May p2/p3 **৪২/৪৩** (১টি সৎ fail — knife-edge bold flip, §৬.৩)।

## ২. সিদ্ধান্ত — OCR-lexicon tiebreaker: DNA-glyph matcher (Round 8), merge স্থগিত

Track C পরিমাপ হিসেবে RapidOCR ব্যবহার করে ৬টি over-split (DEPARTMENT + e-mail ×৫) সঠিকভাবে উদ্ধার করেছে (**৬/৬, ভুল merge ০**) — কিন্তু এটি OCR ব্যবহার করে, আর ব্যবহারকারীর স্থায়ী নির্দেশ **"OCR বাদ দিয়ে"**। বিকল্প তিনটি ছিল: (ক) tiebreaker হিসেবে OCR রাখা, (খ) DNA-glyph টেমপ্লেট-ম্যাচার বানানো (নথির নিজের অক্ষর-আকৃতি দিয়ে পুরো শব্দ মেলানো — OCR-ছাড়া পথ, এখনো বানানো হয়নি), (গ) ৫টি ফিক্স ছেড়ে দেওয়া।

**সিদ্ধান্ত (blanket permission-এর অধীনে, merge-এর): (খ)।** যুক্তি: OCR-কে পেছনের দরজা দিয়ে ঢোকালে "OCR-ছাড়া প্রযুক্তি" দাবিটায় asterisk পড়ে — ব্যবহারকারীর মূল নির্দেশের সঙ্গে আপস হয়। ৬টি merge যাচাইকৃত সঠিক এবং Track C staging-এ ৬/৬ লক্ষ্য হিসেবে রাখা আছে — Round 8-এ DNA-glyph matcher-কে ঠিক এই ৬টি OCR-ছাড়া উদ্ধার করতে হবে। Merge-এ শুধু OCR-মুক্ত অংশ promote করা হয়েছে (S1 speck, Z2, লাল-কালি); r7m seg-এ ৬টি শব্দ ভাঙা অবস্থায় আছে (নমুনার বাইরে — নমুনা ৫১৮/৫১৮-এ এর কোনো প্রভাব নেই)।

## ৩. Track A — প্রতি পাতায় আলাদা লেবেল (b1 + c3)

(রিপোর্ট: `improve/round7/track-a/track-a-report.md`, ২০৯ লাইন)

- **৫টি লেবেল, প্রতিটি নিজের পাতার Lot+WIDTH:** Aug p1 (207/9, **781.5**), Aug p2 (207/9, **776.5** — একই Lot, আলাদা WIDTH, প্রমাণের কেস), May p1 (305/7, **671.5**), May p2 (283/7, **721.5**), May p3 (282/7, **771.5**)। ২টি নতুন delivery staging DB-তে (LSE-0008 Aug, LSE-0009 May)।
- **Migration v1→v2→v3 প্রমাণিত (২৯/২৯):** ২০টি পুরনো audit entry-র hash হুবহু একই, ৭টি পুরনো delivery-র hash এখনো verify হয়, কোনো পুরনো row বদলানো হয়নি; backfill (সব v2 লেবেল → page_no=1) প্রমাণিত; `UNIQUE(delivery_id, page_no)` পরীক্ষিত; `label_ref` এখনো p.1 লেবেল (backward compat); নতুন `delivery_hash v3`-এ per-page labels তালিকা ঢোকে।
- **যাচাই ১৪৬/১৪৬ PASS:** প্রতি পাতার মান ৮২/৮২ (তিনটি স্বাধীন উৎস মিলিয়ে), migration ২৯/২৯, label leak-test (কোনো লেবেলে অন্য পাতার WIDTH/Lot/পুরনো মান নেই — HTML + PDF text দুটোতেই), ৫টি লেবেল PNG ও ৫টি WIDTH-row ক্লিপ চোখে দেখা ("Hard" অক্ষত, doubling নেই)।
- **Domino flow:** পাতা সেভ → সেই পাতার লেবেল — driver + demo পাতা (`domino-per-page.html`) ৫/৫।
- **সীমা:** live পাতায় save→label বোতামের wiring হয়নি (live পাতায় "save"/"label"-এর ০ উপস্থিতি) — Domino driver + demo-তে প্রমাণিত, UI integration বাকি (§৮)। Aug p2-র live পাতা নেই (তার লেবেল seg + edit-state-এর ওপর দাঁড়িয়ে)। May delivery এখনো mechanism test (৩ পাতা ৩টি আলাদা Lot) — তবে per-page লেবেল আসলে এই সমস্যারই সমাধান।

## ৪. Track B — ttfautohint: DO NOT PROMOTE (সৎ নেতিবাচক ফল)

(রিপোর্ট: `improve/round7/track-b/track-b-report.md`, ১৯৪ লাইন)

- **ttfautohint 1.8.4** (Ubuntu noble pool থেকে .deb দিয়ে ইনস্টল — apt mirror আটকে ছিল; Qt deps ছাড়া CLI পুরো কাজ করে)।
- **Default hinting WIDTH match খারাপ করে:** ৩০০ DPI-তে Aug margin **+0.111 → +0.048**, May **+0.088 → +0.060**; neighbourhood mean-ও দুই পাতাতেই কমেছে। কোনো follow-up-ই (hinted @0.97/0.99/1.00, `--stem-width-mode=nnn` @0.98) unhinted @0.98-কে হারাতে পারেনি — Round 6-এর অনুমান (hinting 0.99–1.00 সম্ভব করবে) মাপ দিয়ে খণ্ডিত।
- **Hinting advances/outlines বদলায় না — প্রমাণিত:** সব glyph-এ advance পার্থক্য **০টি**, LSB **০টি**, outline **০টি**; শুধু `cvt/fpgm/gasp/prep` যোগ হয়েছে। আসল ফন্ট অপরিবর্তিত (SHA `187b2dfe…` / `33583cf2…`)। Control run Round 6-এর সংখ্যা হুবহু reproduce করেছে — পরিমাপ বিশ্বস্ত।
- **২০০ DPI:** Aug +0.060→+0.098 (ভালো) কিন্তু May +0.125→+0.049 (খারাপ) — দুই পাতায় উল্টো, নির্ভরযোগ্য লাভ নয়।
- **Browser regression সবুজ:** fontfix **৪৫/৪৫**, verify_round2_300 **১৮/১৮**, repro PASS, manual ১০/১০, identity **৬/৬** — hinting পাতা ভাঙে না, শুধু লাভ নেই। **তাই promoted ফন্ট Round 6-এরটাই আছে (regular `187b2dfe…`, bold `33583cf2…`)।**
- **কারণ-অনুমান (প্রমাণসহ):** ttfautohint outline-কে pixel grid-এ snap করে; DNA glyph scan-এর কালি থেকে trace করা — সেই কালি নিজে hinting ছাড়া rasterize হওয়া ছাপা; grid-snapping প্রতিটি edge ~0.5px সরায়, pixel-IoU কমে।

## ৫. Track C — Vocabulary gate অনুসরণ + Raviraj

(রিপোর্ট: `improve/round7/track-c/track-c-report.md`)

- **PG নমুনা ৫১৮/৫১৮, অতিরিক্ত ০** (R6: ৫২২/৫১৮) — টাইটেল ১৪/১৪, H2 ১৪/১৪; মোট বাক্স ৪২৭৩ → **৪২৩৮ (−৩৫)** (r7 staging, lexicon-সহ)।
- **Speck FP শেষ — নিয়ম S1 (পুনরাবৃত্তি):** ২৭টি ধুলো-বাক্স বাদ, **ভুল বাদ ০** (২৭টির প্রতিটি চোখে দেখা); ১৭টি আসল "-" চিহ্ন অটুট। আকার/ফাঁক দিয়ে আলাদা করা যায় না — প্রমাণসহ বাতিল করা হয়েছে।
- **Piece-attestation (OCR-ছাড়া) — নেতিবাচক ফল, প্রমাণসহ:** টুকরো-মেলানো দুই দিকেই শব্দ-দূষিত (ছোট টুকরোর signature collision) — OCR-ছাড়া কোনো জ্যামিতিক/piece নিয়ম পাওয়া যায়নি। এই ব্যর্থতাই OCR-lexicon tiebreaker-এর দিকে নিয়ে গেছে (§২)।
- **Raviraj p2: ৮৩/১০১ → ৯০/১০১ = ৮৯.১%**; **মোট ৩৩৯/৩৯৪ = ৮৬.০% → ৩৪৬/৩৯৪ = ৮৭.৮%**। N4 **১৭/১৭** — Vehicle/Value ৭টি ফিরেছে (নিয়ম Z2: ১৪/১৪ সত্য, PG লিক ০/২৮)। **Description মেগা-বাক্স ৩ → ০; সঠিক ০/৬৯ → ৩৫/৬৯** (লাল কালি আলাদা করা যায় — PG-তে লাল কালি ০ পিক্সেল)।
- **সৎ সংশোধন:** R6-এর "NAME ✓" ভুল ছিল (লাল স্ট্যাম্প-স্ট্রোকের সঙ্গে মিশে ছিল) — কঠোর গোনায় পুরনো p2 **৮২/১০১**; পুরনো Description "৪/৬৯" গোনাটিও লেবেল-পড়ার ভুল ছিল — আসলে **০/৬৯** ছিল।
- **No-regression:** fontfix ৪৫/৪৫, verify_round2_300 ১৮/১৮, repro300 PASS, manual ১০/১০, write-back ৪১ PASS, identity ১২/১২ (staging-এ)।
- **খোলা:** Description-এর বাকি ৩৪ শব্দ (২৭ merge + ২ ভাগ + SB লাইন ৫ শব্দ বাক্সহীন); Z2 নিয়মটি ৪৫ বাক্সে টিউন করা — আরো পাতায় যাচাই দরকার; N5 অসঙ্গতি (২৬ বনাম ৩১) অমীমাংসিত; p3 পূর্ণ পুনর্গোনা হয়নি।

## ৬. Merge — কী promote করা হয়েছে, কী হয়নি, আর পথে যা ধরা পড়েছে

### ৬.১ Promote করা হয়েছে

- **r7m seg সেট (OCR-মুক্ত):** `improve/round7/merge/segs/` — v5-gate + S1 speck drop + Z2 + লাল-কালি Description। PG মোট ৪২৭৩ → **৪২৪৬ (−২৭)**; নমুনা **৫১৮/৫১৮, অতিরিক্ত ০**; টাইটেল ১৪/১৪, H2 ১৪/১৪ (নিজে চালিয়ে মাপা)। Raviraj p2 ৫৭৪ বাক্স (Track C r7-এর সঙ্গে অভিন্ন)।
- **৪টি live-পাতার source seg আপডেট:** aug-p1 ৩০৫ (অপরিবর্তিত — ০ drop), may-p1 ৩০৯ → **৩০৬**, may-p2 ৩১৩ → **৩০৬**, may-p3 ৩০৮ → **৩০৪**। **৪টি live পাতা rebuild** (Round 6 ফন্ট, FIT_TARGET ০.৯৮ অপরিবর্তিত): Aug SHA `9cf7dee7…`, May `3142dc5f…`, May p2 `fe38f5da…`, May p3 `ec2351d9…` (আগের: `342ab299…` / `4b6b1e4f…` / `7d9f4e1e…` / `78ee2df4…` — সব backup-এ আছে)।
- **`lse_db3.py` shared code-তে promote** (`improve/round3/track-c/lse_db3.py`) — migration v3 + per-page resolver + verify। **শেয়ার্ড DB ফাইল ছোঁয়া হয়নি** (SHA `1c065457…` আগে-পরে একই; ২০ audit entry, LSE-0001–0007)।
- **Verifier expectation আপডেট (মাপা নতুন সংখ্যা, Round 6-এর নিয়ম অনুযায়ী):** fontfix/verify_round2-তে May মোট ৩০৯ → ৩০৬; verify_may23-তে p2/p3 মোট ৩১৩/৩০৮ → ৩০৬/৩০৪।

### ৬.২ Merge-এ ধরা পড়া বিষয় (৩টি আসল আবিষ্কার + ২টি merge বাগ)

1. **May p2/p3-র live seg ছিল stale v4-300 (Round 6-এ promote হয়নি)।** `-300m` ফাইলে v5-gate-এর ৭টি merge ছিল না (p2: ৪টি, p3: ৩টি — সবগুলো vocab-gate v3 MERGE সিদ্ধান্ত হিসেবে যাচাই করা, ৭/৭)। Merge-এ -300m-কে r7m দিয়ে বদলে দেওয়া হয়েছে — p2/p3 পাতা এখন p1-এর মতো একই segmentation পরিবারে (এক v8 সেট, ধারাবাহিক)।
2. **`lse_db3.py`-র path গণনা promote করা অবস্থায় ভুল ছিল।** Track A-র ফাইলে `".." ×3` — সেটা শুধু `improve/round7/track-a/scripts/` (৪ level গভীর) থেকে ঠিক; promoted অবস্থায় (৩ level) এক level বেশি উঠে `scan-paper/round4/track-d` খুঁজত (অস্তিত্ব নেই) — import ভেঙেছিল। Merge-এ root-walking দিয়ে ঠিক করা হয়েছে (শুধু এইটুকুই বদল — diff-এ প্রমাণিত); Track A-র original ছোঁয়া হয়নি।
3. **May p3 WIDTH knife-edge flip (§৬.৩) — একমাত্র লাল চেক।** নিচে বিস্তারিত।
4. **fontfix title-band dust (merge-এ ঠিক করা):** May title-band `[585,630)`-এ highlight-ধুলো (৬×৯ বাক্স `[1008,585,1014,594]`, চোখে দেখা — "ANALYTICAL"-এর ওপরে grey highlight-এর ধুলো, title শব্দ নয়) bold চেকে fail করছিল — S1 speck drop-এ line grouping বদলে তার H1 ট্যাগ হারিয়েছিল। Band-কে "May title boxes" চেকের `[592,630]`-এর সঙ্গে মেলানো হয়েছে (৩টি আসল title শব্দই ভেতরে, cy ~611) — fontfix **৪৩/৪৪ → ৪৩/৪৩**।
5. **আমার নিজের ভুল (ধরা পড়েছে, ঠিক করা হয়েছে):** প্রথম identity-probe ক্লিপে ভুল coordinate ব্যবহার করেছিলাম (WORDS coordinate-কে CSS ধরে — পাতার ~১৫০px offset বাদ গিয়েছিল), ক্লিপে WIDTH সারির বদলে header দেখা গিয়েছিল। চোখে দেখেই ধরা পড়েছে; bounding-rect দিয়ে আবার নেওয়া হয়েছে — প্রক্রিয়াটাই কাজ করেছে।

### ৬.৩ May p3 WIDTH bold flip — সৎ বিশ্লেষণ (৪২/৪৩-এর একমাত্র fail)

**তথ্য:** May p3 WIDTH observation "770.0"-র stroke ratio **০.১৫৬** — নতুন threshold **০.১৫৫২**-র ০.০০০৮ ওপরে (bold), পুরনো threshold **০.১৫৬৪**-র ০.০০০৪ নিচে ছিল (regular)। Seg promotion-এ page median **০.১৩৬০ → ০.১৩৫০** সরেছে — মাত্র ০.০০১। চোখে দেখা: "771.5" আসল regular "770.0"-র চেয়ে সামান্য ভারী render হয় (সূক্ষ্ম কিন্তু সত্যিকারের পার্থক্য)।

**কেন factor বদলে ঠিক করা যায় না (মাপা প্রমাণ):** ratio-র distribution-এ **কোনো gap নেই** — w≥৯, non-heading শব্দে regular সর্বোচ্চ ≈ bold সর্বনিম্ন (Aug ০.১২৬/০.১২৬, May p1 ০.১৫৬/০.১৫৭, p2 ০.১৫৫/০.১৫৬, p3 ০.১৫৬/০.১৫৬)। ১.১৫× threshold একটা continuum-কে ইচ্ছেমতো জায়গায় কাটে; factor বদলালে ছুরির ধার শুধু অন্য শব্দে সরে। **আসল সমাধান: ভালো boldness signal (যেমন document-level median, বা DNA-glyph তুলনা) — Round 8-এর কাজ।** Merge-এ নিয়ম বদলানো হয়নি, p3 promotion ফেরত নেওয়া হয়নি (gate merge + speck drop প্রমাণিত উন্নতি; ফেরত নিলে ভঙ্গুরতা লুকানো হতো, সারত না)।

## ৭. চূড়ান্ত যাচাই টেবিল (merge-এর নিজের re-run — সব সংখ্যা এই রাউন্ডে চালিয়ে মাপা)

| যাচাই | ফল (Round 7 merge) | Round 6 |
|---|---|---|
| fontfix_verify300 | **৪৩/৪৩** (R6: ৪৫/৪৫ — −২ চেক = ২টি ধুলো শব্দ আর title-band চেক নয়, §৬.২-৪) | 45/45 |
| verify_round2_300 | **১৮/১৮** | 18/18 |
| repro300 (doubling) | **PASS** | PASS |
| manual_proof300 | **১০/১০** | 10/10 |
| Identity probe (Lot+WIDTH, ৪টি live পাতা) | **৮/৮** (চোখে দেখা — Lot পরিষ্কার, WIDTH পরিষ্কার, "Hard" অক্ষত, doubling নেই) | 12/12 |
| Write-back (merge build) | **৪১/৪১, FAILURES: none** | 41/41 |
| Write-back (track-a build) | ৩৭/৪১ — **stale Round 4 build** (১২:১৩), আগের ফন্টের PDF বনাম নতুন reference; regression নয় (§৭.১) | — |
| Track D staging | **৪৮/৪৮** (নতুন LSE-0009) | 48/48 |
| Track C staging | **৭৪/৭৪** (নতুন LSE-0013) | 74/74 |
| May multipage | **৫৯/৫৯** (নতুন LSE-0010) | 59/59 |
| May p2/p3 | **৪২/৪৩** — ১ fail: May-p3 WIDTH obs regular (weight=700), knife-edge flip (§৬.৩) | 43/43 |
| sqlcipher | **১৫/১৫** | 15/15 |
| keymgmt | **২৫/২৫** | 25/25 |
| PG sample (r7m seg) | **৫১৮/৫১৮, অতিরিক্ত ০**; টাইটেল ১৪/১৪, H2 ১৪/১৪ | 518/518 |
| Raviraj (r7m seg) | p2 **৯০/১০১ = ৮৯.১%**, মোট **৩৪৬/৩৯৪ = ৮৭.৮%** | 86.0% |

### ৭.১ Write-back ৩৭/৪১ বনাম ৪১/৪১ — বিরোধের সমাধান

Track A ৩৭/৪১ ও Track C ৪১/৪১ — দুজনেই নিজের input-এ সঠিক ছিল: দুটি আলাদা verifier দুটি আলাদা built PDF যাচাই করে। Track-a verifier (`improve/round4/track-a/scripts/`) Round 4-এর built PDF (১২:১৩, Round 5 v1d ফন্টে render করা) যাচাই করে — ৪টি ink-IoU fail (Aug Lot ০.৩১১, Aug WIDTH ০.৪০৭, May Lot ০.৩৩৯, May WIDTH ০.৪১১) — আমি নিজে আবার চালিয়ে একই সংখ্যা পেয়েছি। Merge verifier (`improve/round4/merge/`) Round 6-এ rebuild করা PDF (১৬:০৩, বর্তমান ফন্ট) যাচাই করে — **৪১/৪১** (আমি নিজে চালিয়ে ৪১টি PASS গুনেছি)। বর্তমান প্রমাণ ৪১/৪১; track-a-র ৩৭/৪১ একটি stale staging artifact, regression নয়।

## ৮. সৎ সীমা — এখনো যা সম্পূর্ণ নয় (Round 8-এর প্রার্থী)

1. **May p3 WIDTH knife-edge flip** (§৬.৩) — bold নিয়মের robustness (document-level median বা DNA-glyph তুলনা) Round 8-এর কাজ।
2. **DNA-glyph টেমপ্লেট-ম্যাচার** (§২) — ৬টি OCR-সিদ্ধান্ত merge (DEPARTMENT + e-mail ×৫) OCR-ছাড়া উদ্ধার করতে হবে, ৬/৬ লক্ষ্য।
3. **Live পাতায় save→label বোতামের wiring** — Domino driver + demo-তে প্রমাণিত, browser UI integration বাকি (app shell-এর কাজ)।
4. **Description-এর বাকি ৩৪ শব্দ** (২৭ merge + ২ ভাগ + SB লাইন ৫ শব্দ বাক্সহীন); Z2 নিয়মটি ৪৫ বাক্সে টিউন করা — আরো পাতায় যাচাই দরকার।
5. **০.৯৮ margin মাত্র ২%** — ttfautohint আসল সমাধান নয় (এই রাউন্ডে প্রমাণিত); পরের ধারণা Track B রিপোর্ট §৭-এ।
6. **Aug p2-র live পাতা নেই** — তার লেবেল seg + edit-state-এর ওপর দাঁড়িয়ে।
7. আগের মতোই খোলা (ব্যবহারকারী/আইনজীবী ছাড়া অসম্ভব): print calibration (ফ্যাক্টরির প্রিন্টার), US পেটেন্টের আইনি যাচাই। DBNet swap স্থগিত; DPAPI VM-এ অপ্রমাণিত।

## ৯. ফাইল তালিকা

**এই রাউন্ড (`improve/round7/`):**
- `ROUND7-REPORT.md` — এই রিপোর্ট (এখন `improve/`-তে; মূল কপি এখানে, `improve/round7/`-তে নয় — আগের রাউন্ডগুলোর মতোই)
- `track-a/track-a-report.md` + `scripts/lse_db3.py`, `scripts/migrate_proof.py`, `scripts/run_track_a_r7.py`, `scripts/verify_track_a_r7.py`, `labels/` (৫টি per-page লেবেল), `lse_gravora_r7a.db` (staging v3, ২৯ audit entry), `domino-manifest.json`, `domino-per-page.html`
- `track-b/track-b-report.md` + `dna-r7-*-hinted*.ttf` (DO NOT PROMOTE), `compare_hinted.json`, `final_matcher_r7b.json`, `sweep_hinted.json`
- `track-c/track-c-report.md` + `segs/r7/` (r7 seg, lexicon-সহ), `scripts/apply_r7.py`, `segs/ocr-lexicon.json`, `segs/speck-s1-final.json`
- `merge/apply_r7_merge.py` (OCR-মুক্ত variant), `merge/segs/` (r7m seg — promote করা), `merge/backup/` (৪টি live পাতা + ৪টি source seg + ৩টি verifier + baseline SHA), `merge/sample_rows_r7m.py`, `merge/check_titles_h2_r7m.py`, `merge/probe_identity_r7m.py`, `merge/clips/` (eye-check ক্লিপ)

**Shared tree-তে promote করা (merge-এর):**
- `seg-aug-p1-300.json` (৩০৫, অপরিবর্তিত শব্দ), `seg-may-p1-300.json` (৩০৬), `improve/round4/merge/segs/seg-may-p2-300m.json` (৩০৬), `improve/round4/merge/segs/seg-may-p3-300m.json` (৩০৪)
- `improve/round3/track-c/lse_db3.py` (schema v3 — path-robustness fix-সহ; diff-এ শুধু এইটুকুই)
- `live-scan-page-aug-300.html` (`9cf7dee7…`, ৩০৫ শব্দ), `live-scan-page-may-300.html` (`3142dc5f…`, ৩০৬), `live-scan-page-may-p2-300.html` (`fe38f5da…`, ৩০৬), `live-scan-page-may-p3-300.html` (`ec2351d9…`, ৩০৪)
- `fontfix_verify300.py` (May মোট ৩০৬ + title band `[592,630]`), `verify_round2_300.py` (May মোট ৩০৬), `improve/round6/track-c/scripts/verify_may23_pages.py` (p2/p3 মোট ৩০৬/৩০৪)
- **অপরিবর্তিত:** শেয়ার্ড Round 3 DB (`1c065457…`, ২০ entry, LSE-0001–0007), DNA ফন্ট (`187b2dfe…` / `33583cf2…`), `REPORT.md` / `REPORT-MAY.md` / `ROUND2–6-REPORT.md`, Drive-এ কিছু আপলোড করা হয়নি।

---

*সব সংখ্যা merge-এর নিজের চালানো — যা চালানো হয়নি তা দাবি করা হয়নি। চোখে দেখার দাবি সব clip-এ যাচাই করা। পরিচয় যাচাই row label + box দিয়ে, অবস্থান দিয়ে নয়।*
