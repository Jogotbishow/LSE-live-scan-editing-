# LSE Round 14 রিপোর্ট

**তারিখ:** ২০২৬-১১-০৭ · **স্থান:** `scan-paper/improve/` · **মার্জ ডিরেক্টরি:** `improve/round14/merge-r14/`
**তিন ট্র্যাক সমান্তরালে, একটিই কোঅর্ডিনেটর (এই সেশন), কোনো scheduled job নয়।**

## ০. এক নজরে

| মাপ | R13 | **R14 (মার্জ)** |
|---|---|---|
| Raviraj p2 LINES | ৩১১/৩২৭ | **৩২৭/৩২৭ (+১৬) — সব miss শেষ** |
| A-logo | ৭/২৩ | **২৩/২৩** |
| p2 strict (ক্যানোনিক্যাল redbox) | ৪৩১/৫০২ (৮৫.৯%) | **৪৪৭/৫০২ (৮৯.০%)** |
| p2 strict (সংশোধিত redbox GT) | ৪৮২/৫০২ (৯৬.০%) | **৪৯৮/৫০২ (৯৯.২%)** |
| p2 improved (ক্যানোনিক্যাল / সংশোধিত) | ৪৩৫ / ৪৮৬ | **৪৫১ / ৫০২** |
| p3 strict | ৩৩৪/৩৮৪ (৮৭.০%) | **৩৩৪/৩৮৪ — অপরিবর্তিত (৫০ মিসের সবকটিই artefact, §৩.১)** |
| p3 improved | ৩৮৪/৩৮৪ (১০০.০%) | **৩৮৪/৩৮৪ — অপরিবর্তিত** |
| p3 SPLIT / MERGE / MISS | ০ / ০ / ০ | **০ / ০ / ০** |
| **পূর্ণ পাতা strict (ক্যানোনিক্যাল, হর ৮৮৬)** | ৭৬৫/৮৮৬ (৮৬.৩%) | **৭৮১/৮৮৬ (৮৮.১%)** |
| **পূর্ণ পাতা strict (সংশোধিত GT)** | ৮১৬/৮৮৬ (৯২.১%) | **৮৩২/৮৮৬ (৯৩.৯%)** |
| **পূর্ণ পাতা improved (ক্যানোনিক্যাল)** | ৮১৯/৮৮৬ (৯২.৪%) | **৮৩৫/৮৮৬ (৯৪.২%)** |
| **পূর্ণ পাতা improved (সংশোধিত GT)** | ৮৭০/৮৮৬ (৯৮.২%) | **৮৮৬/৮৮৬ (১০০.০%)** |
| False merge | ০ | **০** |
| Guard check | ৫/৫ PASS | **৫/৫ PASS (merge-r14 seg-এ পুনঃচালিয়ে)** |
| Identity probe | ১৫/১৫ (ক্লিপ ভুল সারি) | **১৫/১৫ — ক্লিপ ফিক্সড, ১৫/১৫ চোখে যাচাই** |
| Live পাতা (৫টি) | R11 SHA-র সঙ্গে identical | **৫/৫ byte-identical — promotion লাগেনি** |
| N5 / Description | ৭৭/৮১ strict, ৮১/৮১ improved / ৬৯/৬৯ | **অপরিবর্তিত — কোনো regression নেই** |
| Redbox | ৬৬/৬৬ (সংশোধিত), ১৫/৬৬ (R9) | **অপরিবর্তিত** |
| VALLEY word-gap নিয়ম | প্রস্তাবমাত্র (universality-র সবচেয়ে বড় পরের ধাপ) | **কাঁচা সেগমেন্টেশনের ডিফল্ট হিসেবে গৃহীত — seg বদলানো হয়নি (§২)** |

**লাভের হিসাব:** LINES +১৬, p2 strict +১৬ (দুই redbox গণনাতেই), পূর্ণ-পাতা strict +১৬, improved +১৬। p2 strict-এর গাণিতিক যাচাই (R12 §১-এর সূত্র: LINES-সঠিক + redbox-সঠিক + অন্যান্য-outside-সঠিক ১০৫): ক্যানোনিক্যাল ৩২৭ + ১৫ + ১০৫ = **৪৪৭** ✓; সংশোধিত ৩২৭ + ৬৬ + ১০৫ = **৪৯৮** ✓; improved = strict + ৪ (N5 improved ৮১/৮১ বনাম strict ৭৭/৮১ — r14m seg-এও পুনরায় মাপা)। পূর্ণ পাতা: ৪৪৭+৩৩৪ = **৭৮১**, ৪৯৮+৩৩৪ = **৮৩২**, ৪৫১+৩৮৪ = **৮৩৫**, ৫০২+৩৮৪ = **৮৮৬** ✓ — মার্জের নিজের পুনঃচালনায় সব মিলেছে।

**সৎ নোট (Track A-র সঙ্গে একমত):** improved-সংশোধিত ৮৮৬/৮৮৬ হলো সূত্রের গাণিতিক ফল (সংশোধিত redbox GT + improved-নিয়মের উদারতা সহ) — রক্ষণশীল সংখ্যা হলো ক্যানোনিক্যাল strict **৭৮১/৮৮৬ (৮৮.১%)**। ১০০% বলতে হলে সংশোধিত GT + improved-নিয়ম দুটোই মানতে হয়; একক সৎ সংখ্যা হিসেবে ৭৮১/৮৮৬-ই বলা উচিত।

## ১. Track A — A-logo ১৬ rescue (সম্পূর্ণ)

**নতুন seg:** `improve/round14/track-a/seg-rav-p2-r14m.json` (৫৫৭ শব্দ; r13m ছিল ৫৫৫; SHA `9c539181…`) — **এটাই এখন ক্যানোনিক্যাল Raviraj p2 seg** (merge-r14/segs/-এ কপি করা হয়েছে, SHA মিলেছে)।
**পদ্ধতি:** r13m-এর কপি থেকে ১৪টি fragment বাক্স সরিয়ে ১৬টি হাতে-মাপা কালি-সীমা বাক্স যোগ (segmenter-mask tight-band + CC + rule-strip, overlay চোখে যাচাই ১৬/১৬)। কাজের ফ্রেম `improve/round4/merge/rav/rav-p2-300-rot.png` (৩৫০৮×২৪৮০, deskewed/rotated) — raw `rav-p-02.png`-এর সঙ্গে seg coordinate মেলে না।

**শ্রেণি অনুযায়ী ফল (১৬/১৬):** (ক) merge ৭/৭ — MATA, Nothing's, MAA, ANNAPURNA, TRANSPORT, AGENCY, known, as: (শেষ দুটি box [467,527,578,544]-এর ভাঙন); (খ) দৈত্য-CC rescue ৪/৪ — SERVICE, REG., NO., AADCM0917AST001 (rule-সারি/কলাম strip করে পুনরায় CC — অক্ষর আলাদা হয়েছে, একটিও হারায়নি); (গ) box-৯২ split ৪/৪ — 26-05-2006, •, CIN:, U60231BR1998PTC008558; (ঘ) LOGO-zone ১/১ — M (নিচে §১.১)।

**False merge ০ — মার্জের নিজের যাচাই:** diff ঠিক ১৪টি সরানো + ১৬টি যোগ (মার্জ নিজে গুনেছে: পুরনো ৫৫৫ → নতুন ৫৫৭, এর বাইরে আর কোনো পুরনো বাক্স হারায়নি, ০টি)। নতুন-বনাম-বেঁচে-থাকা overlap শুধু ১টি — Nothing's বনাম 'far' (y৩৩১–৩৩২) — উত্তরাধিকারসূত্রে পাওয়া (পুরনো fragment বাক্সও একই জায়গায় overlap করত; কালি সংঘর্ষ করে না)। মার্জ নিজে দুটি overlay চোখে দেখেছে: `new-service-2x.png` (SERVICE/REG./NO./AADCM/26-05-2006/•/CIN:/U60231… — প্রতিটি বাক্স ঠিক একটি শব্দ ঢাকে) ও `new-top-2x.png` (MATA + Nothing's — M-এর নীল কালি ও ATA এক বাক্সে)।

### ১.১ LOGO-zone সিদ্ধান্ত — WHITELIST (surgical, এই seg-এই শুধু)

**সিদ্ধান্ত: M-এর কালি এই seg-এ ব্যবহার করা হয়েছে; `segment.py` বা zone বদলানো হয়নি।** মাপা কারণ: M আসল অক্ষর, গ্রাফিক নয় (CC (400,274,112,109), area ৯৩৯৩; কালির mean BGR [191,140,95] A-র [189,140,96]-এর সঙ্গে হুবহু এক; একই baseline/উচ্চতা); zone (150,120,510,450) শব্দটিকে মাঝখানে কেটেছে (M-এর কেন্দ্র ভেতরে, ATA বাইরে) — সীমানাটি arbitrary; logo গ্রাফিক (swoosh, box [532,399,752,500]) ছোঁয়া হয়নি, আগের মতোই unboxed। Scope surgical — PG-সহ অন্য কোনো পাতায় প্রভাব নেই (PG sample ৫১৮/৫১৮ দিয়েই প্রমাণিত)। **সিদ্ধান্ত বদলানো যায়** — MATA-কে miss হিসেবে ফিরিয়ে নিলে LINES ৩২৬/৩২৭ হবে, আর কিছু বদলাবে না। অবশিষ্ট ঝুঁকি: M logo letterform — retype-এ font-match আনুমানিক হবে; M|A ফাঁক ২২px logo letter-spacing।

### ১.২ Regression যাচাই (মার্জের নিজের পুনঃচালনা)

N5 strict **৭৭/৮১**, improved **৮১/৮১**; Description r10 GT **৬৯/৬৯, wrong ০** (মার্জ নিজে `--gt` দিয়ে চালিয়েছে), পুরনো R9 GT **৬৩/৬৯, একই ৬টি ভুল**; redbox নতুন scorer **৬৬/৬৬**, R9 ক্যানোনিক্যাল **১৫/৬৬**; PG sample **৫১৮/৫১৮, ০ extra** (merge-r14 seg-এ চালিয়ে)। সব R13-র সমান — কোনো regression নেই।

### ১.৩ সৎভাবে যা বাকি (Track A-র §৪, মার্জের সঙ্গে একমত)

1. **Nothing's/far box-overlap** — উত্তরাধিকারসূত্রে পাওয়া; inpainting-এ far-র ascender-শীর্ষের ২ সারি ঝুঁকি (E-ce y-overlap-এর একই শ্রেণি, §৩.৩ দেখুন)।
2. **DATED ভার্ডিক্ট-কুইর্ক (আগে থেকে ছিল, ছোঁয়া হয়নি):** verdicts-এ DATED 'correct' কিন্তু তার box হিসেবে লেখা [826,598,984,623] — সেটি আসলে CHARGES-এর বাক্স। আসল DATED বাক্স [925,553,990,581]। আরও: D-র stem-এর CC (907,554,17,29) বাক্সের বাইরে (৯০৭ < ৯২৫)। LINES-তালিকায় প্রভাব নেই (DATED 'correct'-ই আছে)।
3. **Formerly 'ok' কুইর্ক (আগে থেকে ছিল, ছোঁয়া হয়নি):** বাক্স [360,521,393,544] শুধু "For" ঢাকে — "merly" ধূসর অক্ষর unboxed। LINES-তালিকায় প্রভাব নেই, কিন্তু GT-র সঙ্গে মেলে না — পরের রাউন্ডে verdict-ফাইলের এই দুটি entry (Formerly, DATED) যাচাই করা উচিত।

## ২. Track B — page-adaptive word-gap নিয়ম: VALLEY (গৃহীত — কাঁচা সেগমেন্টেশনের ডিফল্ট হিসেবে)

**নিয়ম (VALLEY):** পৃষ্ঠার নিজের within-line ফাঁকের হিস্টোগ্রামে অক্ষর-ফাঁকের চূড়া (mode1) আর শব্দ-ফাঁকের চূড়ার (mode2) মাঝের উপত্যকার তলদেশই থ্রেশহোল্ড। গার্ড [0.15, 1.0]×med_h; ডিজেনারেট হলে পুরনো স্থির নিয়মে ফলব্যাক। কোনো হাতে-টিউন করা মান নেই — mode1/mode2/উপত্যকা সবই পৃষ্ঠার নিজের ফাঁক থেকে মাপা। বাস্তবায়ন: `segment_valley.py` / `segment_u_valley.py` (ডিফল্ট valley; শেয়ার করা `segment.py` / `segment_u.py` অপরিবর্তিত)।

**মার্জের নিজের পুনঃচালনা (ফ্রেশ বেসলাইন বনাম VALLEY — একই কোড, শুধু থ্রেশহোল্ড আলাদা):**

| পরীক্ষা | ফ্রেশ বেসলাইন | VALLEY |
|---|---|---|
| PG স্যাম্পল রো / ৫১৮ | ৫২৮ (+১০) | **৫২৭ (+৯)** |
| Raviraj p2 LINES / ৩২৭ | ২৯৩ | **২৯৩** |
| N5 strict / improved / ৮১ | ১৫ / ১৮ | **২৫ / ২৮** |
| Description / ৬৯ | ৭ | **১৬** |
| Raviraj p3 strict / improved / ৩৮৪ | ২৪০ / ২৮০ | **২৫০ / ২৯৩** |

**ইউনিভার্সালিটি strict (একই হর, Track B-র হাতে-গোনা — মার্জ per-line যোগফল মিলিয়ে যাচাই করেছে):** Tottel ১৭/২৪ (৭০.৮%) → **১৭ (অপরিবর্তিত — ডিজেনারেট ফলব্যাক ফায়ার করেছে)**; FUNSD ১৮/৩৮ (৪৭.৪%) → **২৫/৩৮ (৬৫.৮%, +১৮.৪ পয়েন্ট)**; SROIE ৩/১৬ (১৮.৮%) → **৫/১৬ (৩১.৩%)**; Shields ১২/২৫ (৪৮.০%) → **১০/২৫ (৪০.০%, −২ — valley থ্রেশহোল্ড ৬ "wanted" ও "and"-কে ভেঙেছে)**।

**সবচেয়ে গুরুত্বপূর্ণ সতর্কতা (Track B-র নিজের, মার্জের সঙ্গে একমত — লুকানো হয়নি):** প্রকাশিত r10m/r13m seg কাঁচা `segment.py` আউটপুট নয় — তাতে মার্জ পাইপলাইনের পোস্ট-প্রসেসিং আছে (ভোকাব-গেট v3, হাতে-মার্জ)। তাই কাঁচা বেসলাইন প্রকাশিত সংখ্যার চেয়ে কম স্কোর করে (LINES ২৯৩ বনাম ৩১১, N5 strict ১৫ বনাম ৭৭)। **বৈধ তুলনা ফ্রেশ-বেসলাইন বনাম VALLEY** — সেই তুলনায় VALLEY-র কোনো রিগ্রেশন নেই, তিনটিতে উন্নতি। কিন্তু VALLEY প্রকাশিত r13m/r14m স্তরে পৌঁছায় না।

**মার্জের সিদ্ধান্ত (প্রস্তাব হিসেবে, পরিবর্তনযোগ্য): VALLEY গৃহীত — কাঁচা সেগমেন্টেশনের নতুন ডিফল্ট হিসেবে, প্রকাশিত seg-এর বিকল্প হিসেবে নয়।** অর্থাৎ: r13m/r14m seg-ই ক্যানোনিক্যাল থাকবে; পরের রাউন্ড থেকে কাঁচা সেগমেন্টেশন `segment_valley.py` দিয়ে চলবে, আর মার্জ পাইপলাইনের পোস্ট-প্রসেসিং আগের মতোই থাকবে। বাতিল বিকল্প: otsu (PG LINES ২৯৩→২৭৯ −১৪, N5 ১৫→১০, Tottel ১৭→১৩); kmed (PG-তে valley-র সমান ভালো হলেও Shields-এ বিপর্যয় — থ্রেশহোল্ড ৫৯px, ৩/২৫)। **জানা সীমা:** aug-p8 "SALES DEPARTMENT" ভুল মার্জ (বোল্ড অক্ষর-ফাঁক ৯px = শব্দ-ফাঁক — শুধু ফাঁকের আকার দিয়ে আলাদা করা যায় না); দশমিক এখনো ভাঙে (SROIE/FUNSD); Tottel-এ ইটালিক অক্ষর-ফাঁক শব্দ-ফাঁক ছাড়ায়; FUNSD "Associates" লাইন-গ্রুপিংয়ের ভাঙন — ফাঁকের নিয়মের বাইরে।

## ৩. Track C — p3 strict median-y তদন্ত + প্রোব ক্লিপ ফিক্স + E-ce y-overlap নোট (সম্পূর্ণ)

### ৩.১ p3 strict ৫০ মিস: আসল ০, artefact ৫০ — improved-ই সৎ মাপ, এখন প্রমাণসহ

৫০টির ৫০টিতেই লাইনের ব্যান্ডের ভেতরে x-মিলে যাওয়া সঠিক বাক্স আছে, improved-এ পাস করে, CC cover ০.৭৮–১.০০। Mechanism: TOP ২৩, BIG ১৭, SMALL ৬ (ক্ষুদ্র বিরামচিহ্ন), BOTTOM ৩, MID ১। ৫০টির কোনোটিতেই মিস-বাক্স তার নিজের median block-এ নেই (০/৫০) — median সবসময় লাইনের অন্য ফন্ট-উপদলের। ২১টি আক্রান্ত লাইনের overlay স্ট্রিপ চোখে যাচাই করা (২১/২১)। IRC/BIN নতুন median see-saw রিগ্রেশন, বাক্স byte-identical r10m→r13b — ইচ্ছে করে ঠিক করা হয়নি (scorer-gaming এড়াতে, R13-র সিদ্ধান্তের মতো)। **নতুন seg নেই, GT পরিবর্তন ০। p3 strict ৩৩৪/৩৮৪ (৮৭.০%), improved ৩৮৪/৩৮৪ (১০০.০%) — মার্জ নিজে scorer পুনঃচালিয়ে নিশ্চিত।** একটি পদ্ধতিগত নোট (Track C-র প্রথম পাসের ভুল, ধরা পড়েছে): x-শুধু মিলিয়ে খুঁজলে পাশের লাইনের ভুল বাক্স ধরা পড়ে (প্রথম পাসে ১৩টি ভুল) — মিল সবসময় ব্যান্ড-সীমাবদ্ধ হতে হবে। **রায়: p3-র জন্য improved-ই সৎ মাপ — এটা এখন প্রমাণসহ বলা যায়।**

### ৩.২ প্রোব ক্লিপ বাগ ফিক্সড — এখন ক্যানোনিক্যাল প্রোব

**মূল কারণ (মাপা):** পুরোনো সূত্র ধরে নিয়েছিল `.wd` এলিমেন্ট document origin-এ বসে; আসলে পাতা ৩৭px ডানে (centering: (৯০০−৮২৬)/২) ও ১৫০px নিচে (sticky বার ১৩২px + margin ১৮px) বসে — তাই পুরোনো ক্লিপ ঠিক এক সারি উপরের লেখা দেখাত (Lot ক্লিপে "Document No. PGFL…" হেডার, WIDTH ক্লিপে "FILLUP BY SALES DEPARTMENT / P.O. No." সারি)। **ফিক্স:** ক্লিপ এখন `getBoundingClientRect()` + scroll অফসেট থেকে (একই evaluate কলে text/bg/rect), কোনো `//3` নেই; Hard-এরও ক্লিপ যোগ হয়েছে। Guard FULL আগে চালানো — ৫/৫ PASS। **মার্জের নিজের পুনঃচালনা (merge-r14/verifiers/probe_identity_r14m.py, merge-r14 seg-এ): ১৫/১৫ PASS** — মার্জ নিজে Aug p2 WIDTH ক্লিপ চোখে দেখেছে (৭৭৬.৫ পরিষ্কার, "Hard" অছোঁয়া, doubling নেই) আর May p1 WIDTH ক্লিপ চোখে দেখেছে (৬৭১.৫ bold পরিষ্কার)। **এই ফিক্সড প্রোবই এখন ক্যানোনিক্যাল** — পুরনো r13m প্রোবের ক্লিপ-সূত্র আর ব্যবহার করা যাবে না।

**মার্জের নিজের ধরা (পথে পাওয়া বাগ, ঠিক করা হয়েছে):** প্রথম repoint-এ শুধু joined-ফর্ম পাথ (`round13/merge-r13`) বদলেছিল — `os.path.join` ফর্মের M10/MG লাইন বদলায়নি, ফলে প্রোবের প্রথম মার্জ-রান ক্লিপ track-c/-তে লিখেছিল। grep দিয়ে ধরা পড়েছে; দুই ফর্মই বদলে আবার চালানো হয়েছে — এখন ক্লিপ + JSON merge-r14/-তেই লেখা হয়। একই ভুল বিল্ডার repoint-এও ছিল (প্রথম sed-এ aug1-এর M10 বদলায়নি) — সেটাও grep দিয়ে ধরে ঠিক করা হয়েছে। শিক্ষা: repoint-এর পর `grep round13` দিয়ে যাচাই করা বাধ্যতামূলক।

### ৩.৩ E-ce y-overlap নোট (inpainting-এর জন্য — মাপা, seg বদলানো হয়নি)

Raviraj p2 "Consignee Bank's Name and Address" ব্লক: লেবেল সারি L41 (ধূসর, ৩৫–৪৫px, baseline y১৪৬৪) × মান সারি L42 (কালো, ১৭–২০px, cap-top y১৪৫৫) — **৯টি overlap জোড়া**, y-overlap ৯px (৮টি) ও ২০px (৩টি, "Consignee" বাক্সের নিচে); অন্য সারি-জোড়ায় overlap ০। "Consignee" বাক্সের বাড়তি ১১px (y১৪৭৫) লেবেলের একমাত্র descender 'g' — ৪× zoom-এ চোখে নিশ্চিত। **inpainting-এর অর্থ: বাক্স-rect মুছে ফেলা অনিরাপদ** (অন্য সারির কালি মুছে যাবে), ক্রম দিয়ে ঠেকানো যাবে না — **শব্দের নিজের CC-মাস্ক দিয়ে মুছতে হবে**, আর overlap জোনে ধূসর-লেবেল বনাম কালো-মান টোন-পার্থক্যই সারি আলাদা করার সংকেত। এটা নোট মাত্র — কোনো seg বদলানো হয়নি।

## ৪. মার্জ — একটি সামঞ্জস্যপূর্ণ v8 পাতা সেট

**Seg পরিবার (merge-r14/segs/, ১৬টি):** r10m PG seg ১৪টি (r13m-এর সঙ্গে byte-identical, `cmp` দিয়ে যাচাই করা) + Track A `seg-rav-p2-r14m.json` (৫৫৭ শব্দ, SHA `9c539181…` — track-a-র ফাইলের সঙ্গে মিলেছে) + Track B-র কিছু বদলায়নি + Track C-র p3 seg অপরিবর্তিত (`seg-rav-p3-r13b.json`, ৪০০ বাক্স)। তিন ট্র্যাক ভিন্ন জিনিস বদলেছে (p2 seg / কাঁচা নিয়ম / কিছুই না) — কোনো সংঘাত নেই। PG seg ছোঁয়া হয়নি।

**Live পাতা rebuild (r14m builder, merge-r14/pages/-এ): ৫/৫ byte-identical** root-এর সঙ্গে (Aug p1 `bce37147…`, Aug p2 `f4f72713…`, May p1 `d0948b0f…`, May p2 `539995a9…`, May p3 `8587be86…`)। **PG পাতায় কোনো পরিবর্তন নেই — promotion লাগেনি, re-upload লাগবে না।** Heading JSON ৫/৫ R13-র সঙ্গে identical। (May23 builder-এ পাতা-আর্গুমেন্ট দিতে হয় — `may2` ও `may3` আলাদা করে বানানো হয়েছে, R13-র মতোই।)

**মার্জের নিজের পুনঃমাপ (track রিপোর্টের সংখ্যা নয়, merge ফাইলে চালানো):** LINES ৩২৭/৩২৭ (`rescore_lines_r14a.py`); redbox নতুন scorer ৬৬/৬৬, R9 canonical ১৫/৬৬; p3 strict ৩৩৪/৩৮৪, improved ৩৮৪/৩৮৪, SPLIT/MERGE/MISS ০, FP ১৬; N5 ৭৭/৮১ strict, ৮১/৮১ improved; Description (r10 GT) ৬৯/৬৯, wrong ০; Lot-anchor ১৪/১৪ (নিচে §৫); Guard ৫/৫ PASS + stale FAIL (R13-র প্রমাণ বহাল); VALLEY ফ্রেশ-বনাম-ফ্রেশ যাচাই (§২)। **পূর্ণ পাতা (হর ৮৮৬): strict ক্যানোনিক্যাল ৭৮১, সংশোধিত ৮৩২; improved ক্যানোনিক্যাল ৮৩৫, সংশোধিত ৮৮৬।**

**Description-নোট (সৎ স্পষ্টকরণ, R13-র মতোই):** পুরনো R9 GT দিয়ে scorer দেয় ৬৩/৬৯ (৬টি ভুল: L3:QUANTITY, UNIT, PRICE, USD, 5.80/KG.., L4:CPT) — কিন্তু r13m আর r14m **দুটোতেই একই ৬৩/৬৯**, অর্থাৎ regression নয়, GT-সংস্করণের পার্থক্য। Canonical r10 GT-তে ৬৯/৬৯ দুটোতেই।

## ৫. যাচাই সারণি (কোঅর্ডিনেটরের নিজের পুনঃচালনা)

| চেক | ফল |
|---|---|
| fontfix_verify300.py | **৪৩/৪৩ PASS** |
| verify_round2_300.py (rebuild RETIRED) | **১৮/১৮ PASS × ২ ধারাবাহিক রান** — root পাতার SHA + mtime suite-র আগে/পরে অপরিবর্তিত |
| repro300.py | **PASS** — ২টি edited span, exact text, .done, no doubling |
| manual_proof300.py | **১০/১০ PASS** |
| Guard check (full মোড, merge-r14 seg) | **৫/৫ PASS, exit ০** (C1–C5 সব) |
| identity probe (ফিক্সড ক্লিপ, merge-r14) | **১৫/১৫** — Lot+WIDTH+Hard × ৫, ক্লিপ চোখে যাচাই করা (Aug p2 WIDTH ৭৭৬.৫ পরিষ্কার, May p1 WIDTH ৬৭১.৫ bold পরিষ্কার, Hard অছোঁয়া) |
| write-back | **৪১/৪১ + ৪০/৪০, FAILURES: none** (৪০/৪০ = R10 work verify_rebuild_300.py; verify_writeback300_r10.py-তেও ৪১টি [PASS] লাইন — দুটি ভেরিফায়ার ভিন্ন PDF মাপে, পিক্সেল-গণনা সামান্য আলাদা) |
| Track D staging | **৪৮/৪৮** ([PASS] লাইন ৪৮, FAILURES: none) |
| Track C (R5) staging | **৭৪/৭৪** ([PASS] লাইন ৭৪, FAILURES: none) |
| May multipage | **৫৯/৫৯** ([PASS] লাইন ৫৯, FAILURES: none) |
| May p2/p3 (r11m verifier) | **৪৩/৪৩ PASS** |
| sqlcipher_test.py | **১৫/১৫** ([PASS] লাইন ১৫, FAILURES: none) |
| keymgmt_proof.py | **২৫/২৫** ([PASS] লাইন ২৫, FAILURES: none) |
| save→label LIVE (১৮/পাতা × ৫) | **৯০/৯০** |
| Aug p2 (r10m verifier, root) | **১৬/১৬** (Hard neighbour untouched) |
| heading R1 (check_heading_r11.py) | **PASS ১৪/১৪ × ৩ family** (TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০; control-এ H1-diff ২ প্রত্যাশিত) |
| sample rows (merge-r14 seg, r10m) | **৫১৮/৫১৮, ০ extra** |
| N5 (r10 scorer, merge seg) | **৭৭/৮১ strict, ৮১/৮১ improved** — অপরিবর্তিত |
| Description (r10 GT, merge seg) | **৬৯/৬৯, wrong ০** — অপরিবর্তিত |
| redbox নতুন scorer (merge r14m seg) | **৬৬/৬৬** |
| redbox canonical R9 scorer (merge r14m seg) | **১৫/৬৬** |
| p3 re-score (merge GT, merge r13b seg) | **strict ৩৩৪/৩৮৪ (৮৭.০%), improved ৩৮৪/৩৮৪ (১০০.০%)** |
| LINES verdicts (merge copy) | **৩২৭/৩২৭** |
| Lot-anchor (merge পুনঃচালনা) | **১৪/১৪, gap +০.০১২৯৫৩, LOPO ১৪/১৪, thinnest ০.০০৬৩৫৯** |
| VALLEY ফ্রেশ-বনাম-ফ্রেশ (merge পুনঃচালনা) | LINES ২৯৩→২৯৩, sample ৫২৮→৫২৭, N5 ১৫/১৮→২৫/২৮, p3 ২৪০/২৮০→২৫০/২৯৩ |
| live পাতা rebuild | **৫/৫ byte-identical** R11/R12/R13 promotion SHA-র সঙ্গে |
| shared DB (read-only) | **SHA 1c065457… অপরিবর্তিত, ২০ audit entry, chain linked, ৭ delivery (LSE-0001–0007)** |

**পরিবেশ-নোট:** R14-এ কোনো নতুন পরিবেশ-পরিবর্তন হয়নি (R13-র Track C-র `pip install --user opencv-python-headless` — numpy ১.২৬.৪ → ২.৫.৪ — আগের মতোই আছে; মার্জের পুরো suite venv থেকে চালিয়ে পাস করেছে)।

**Round 3-র পুরনো verify_rebuild_300.py এখনো তার ৪টি known ink-IoU fail দেখায়** (v1 staging artifact, ২৯/৩৩) — superseded artifact, regression নয়; বর্তমান R10 work/verify_rebuild_300.py ৪০/৪০ PASS (উপরে)।

## ৬. সৎ miss ও এখনো খোলা

- **Nothing's/far box-overlap** (§১.৩) — উত্তরাধিকারসূত্রে পাওয়া; inpainting-এ ২ সারির ascender-শীর্ষ ঝুঁকি।
- **DATED + Formerly ভার্ডিক্ট-কুইর্ক** (§১.৩) — আগে থেকে ছিল; পরের রাউন্ডে verdict-ফাইলের এই দুটি entry যাচাই করা উচিত।
- **p3 strict ৫০টি** — median-y নিয়মের সীমা (§৩.১); strict scorer বদলানো ছাড়া ঠিক করা যাবে না, আর median-কে টেনে ফেরানো scorer-gaming হবে। p3-র জন্য improved-ই সৎ মাপ, এখন প্রমাণসহ।
- **VALLEY-র সীমা** (§২): Shields −২, aug-p8 SALES DEPARTMENT ভুল মার্জ, দশমিক এখনো ভাঙে, Tottel অপরিবর্তিত।
- **E-ce y-overlap** (§৩.৩) — ৯ জোড়া; inpainting-এ CC-মাস্ক লাগবে, box-rect নয়।
- **Lot-anchor PG-only** — নতুন template-এ GT-decided পুনঃযাচাই ছাড়া ০.০৩৬ প্রয়োগ করা যাবে না (R13-র সিদ্ধান্ত বহাল)।
- **আগের মতোই খোলা:** print calibration (factory printer — শুধু ব্যবহারকারী করতে পারেন), US patent legal check (lawyer-এর কাজ; Adobe US9741142B2 সবার আগে দেখতে হবে), DBNet swap deferred (KEEP CLASSICAL), DPAPI VM-এ অপ্রমাণিত, `raviraj COA 20 micron.jpg` পাওয়া যায়নি, ২৫টি অন্য PDF পাতা শুধু contact-sheet দেখা, redbox L5 'and'-এর শুধু 'a' বাঁচে ('nd'-তে কালি নেই), সাধারণ bold classification এখনো অমীমাংসিত।
- **খোলা product সিদ্ধান্ত:** ১৮টি borderless edge (faithful বনাম বন্ধ করা); integration design-এর Q-03–Q-09; DEEP-RESEARCH §১১-এর বাকি সিদ্ধান্ত।
- **যাচাইয়ের সীমা (সৎ নোট):** Track B-র ইউনিভার্সালিটি সংখ্যা (FUNSD/SROIE/Tottel/Shields) হাতে-গোনা — মার্জ per-line যোগফল মিলিয়ে আর PG-দিকের ডেল্টা পুনঃচালিয়ে যাচাই করেছে, কিন্তু প্রতি শব্দের হাতে-গোনা নিজে আবার গোনেনি।

## ৭. ফাইল

- **এই রিপোর্ট:** `improve/ROUND14-REPORT.md` (কপি: `improve/round14/merge-r14/ROUND14-REPORT.md`)
- **মার্জ ডিরেক্টরি:** `improve/round14/merge-r14/` — `segs/` (পূর্ণ বর্তমান পরিবার: ১৪ PG + r14m p2 + r13b p3), `gt/` (redbox_groups_r12, rav-p3 GT r12, n5 GT r10, r13a_gt), `pages/` (৫টি rebuild পাতা, root-এর সঙ্গে byte-identical), `cleans/` (r13m থেকে কপি) + `exemplar-pg.npy`, `heading-*-300-r13m.json` (৫টি, R13-র সঙ্গে identical), `scripts/` (৪টি r14m builder + `guard_check.py` + `identity_pg.json` + `rescore_lines_r13m.py`), `verifiers/` (r11m verifier-দের কপি + `probe_identity_r14m.py` + `verify_aug2_page_r10m.py` + `check_heading_r11.py`), `clips/` (১৫টি r14m ক্লিপ + Aug p2 ১৬/১৬ প্রমাণ-ক্লিপ ৪টি), `guard-*.json` (৫টি), `verdicts-r14m.json`, `backup/` (r13m p2 seg + r13b p3 seg কপি)
- **Track A:** `improve/round14/track-a/` (TRACK-A-REPORT.md, seg-rav-p2-r14m.json, r14a_gt.json, verdicts-r14a.json, checks-r14a.txt, scripts/, clips/)
- **Track B:** `improve/round14/track-b/` (TRACK-B-REPORT.md, segment_valley.py, segment_u_valley.py, segment_r14b.py, segment_u_r14b.py, segs-baseline/, segs-valley/, segs-otsu/, segs-kmed/, segs-kmed25/, diff_summary_valley.txt, uni_counts.json, pg_scores_all_modes.txt, স্কোরার/বিশ্লেষণ স্ক্রিপ্ট, strip/zoom/crop প্রমাণ)
- **Track C:** `improve/round14/track-c/` (TRACK-C-REPORT.md, probe_identity_r14m.py + probe_identity_r14m.json, clips/ ১৫টি, investigate_p3_strict.py, classify2_p3_strict.py, strict50_r14c.json/.txt, score_p3_r14c.py, make_p3_strips.py, overlays/ ২১টি p3 স্ট্রিপ + ece প্রমাণ, guard-*.json ৫টি)

**ছোঁয়া হয়নি:** কোনো live পাতা (root), কোনো shared seg/verifier/builder, shared DB (শুধু read-only যাচাই), REPORT.md / REPORT-MAY.md / ROUND2–13-REPORT.md, Google Drive-এ কিছু আপলোড করা হয়নি। কোথাও OCR নেই।

## ৮. পরের রাউন্ডের প্রস্তাব (সিদ্ধান্ত নয় — প্যারেন্টের জন্য)

1. **DATED + Formerly ভার্ডিক্ট-কুইর্ক** — verdict-ফাইলের দুটি entry যাচাই/ঠিক করা (§১.৩)।
2. **VALLEY-র আসল পরীক্ষা** — কাঁচা VALLEY + মার্জ পাইপলাইনের পোস্ট-প্রসেসিং একসঙ্গে চালিয়ে দেখা r14m-এর ৩২৭/৩২৭ ছাড়ায় কি না (এখনো প্রমাণ হয়নি যে VALLEY প্রকাশিত স্তরে কিছু যোগ করে)।
3. **দশমিক (Rule D)** — এখনো সব জায়গায় ভাঙে (SROIE, FUNSD, Raviraj p2) — ফাঁকের নিয়মের বাইরে আলাদা নিয়ম দরকার।
4. **aug-p8 SALES DEPARTMENT বোল্ড-ফাঁক টাই** — ফাঁকের আকার ছাড়া আরেকটি সংকেত (যেমন অক্ষরের প্রস্থ/উচ্চতা অনুপাত) দরকার।
5. **Inpainting CC-মাস্ক নিয়ম বাস্তবায়ন** — E-ce + Nothing's/far overlap কেসে box-rect মুছে ফেলার বদলে CC-মাস্ক দিয়ে মোছা (§৩.৩) — Raviraj-ধরনের পাতায় আসল এডিটিংয়ের দিকে পরের প্রকৌশল ধাপ।
