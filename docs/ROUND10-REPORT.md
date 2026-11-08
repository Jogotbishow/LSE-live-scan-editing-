# LSE — Round 10 রিপোর্ট (মার্জ)

**তারিখ:** ২০২৬-১১-০৭ | **মার্জ ডিরেক্টরি:** `improve/round10/merge-r10/` | **স্ট্যাটাস:** সম্পূর্ণ — ৫টি live পাতা root-এ promote করা হয়েছে।

## ১. সারাংশ — এক নজরে

| বিষয় | Round 9 | **Round 10 (মার্জ)** |
|---|---|---|
| N5 (Raviraj p2) | ৫৭/৮১ | **৮১/৮১** (improved scorer); strict ৭৭/৮১ |
| Description | ৬৯/৬৯ (বৃত্তাকার GT-তে) | **৬৯/৬৯, ০ error — এখন কালি-যাচাইকৃত GT-তে** |
| Raviraj পূর্ণ-পাতা | ৫৬০/৭৯৫ = ৭০.৪% | **৫৯১/৭৯৫ = ৭৪.৩%** strict; ৫৯৫/৭৯৫ = ৭৪.৮% improved |
| May p2/p3 | ৪২/৪৩ (knife-edge) | **৪৩/৪৩ — knife-edge সমাধান** |
| fontfix_verify300 | ৪৩/৪৩ | **৪৩/৪৩** |
| Write-back (পুনর্নির্মিত) | ৩৭/৪১ (পুরোনো staging) | **৪১/৪১, FAILURES: none** |
| Live পাতা | ৫টি | **৫টি — সব নতুন (www মার্জ + (B) + May WIDTH bold)** |
| শেয়ার্ড DB | SHA 1c065457… | **অপরিবর্তিত — SHA 1c065457…, ৭ delivery, ২০ audit** |

**মার্জের সবচেয়ে বড় ধরা:** Track B-র (B) নিয়ম আর Track C-র www মার্জ — আলাদাভাবে দুটোই ১০০% যাচাইকৃত — **একসঙ্গে চললে aug-p2/p3-র হেডার লাইন H1 থেকে পড়ে যায়** (§৫ দেখুন)। কোনো একক বা দ্বিমাত্রিক threshold r10m-এ হেডার আলাদা করতে পারে না (সব মাপা)। সমাধান: heading লাইন-স্তরের বৈশিষ্ট্য — (B) নিয়ম দিয়ে r9m seg থেকে হিসাব করে r10m শব্দ-তালিকায় প্রয়োগ। Round 9-র §৫.৩ হার্ডকোড override **সরানো হয়েছে**।

## ২. Track A — দশমিক-বিন্দু ভাঙন + N5 (সম্পূর্ণ)

- **N5: ৫৭/৮১ → ৭৭/৮১ (strict), ৮১/৮১ (improved scorer)।** ২৪টি miss-ই ধরন অনুযায়ী ঠিক: Merge ৭, Split ৬, Truncated ৫, Colon ৩, y-বিচ্যুতি ৩ (scorer-ঠিক)। Strict ৭৭ বনাম improved ৮১: strict scorer লাইন median-y ব্যবহার করে (বৃত্তাকার — seg থেকেই বানানো); ৪টি বাক্স GT-র সঙ্গে হুবহু মিললেও strict-এ ফেল করে (Reg., pay, Consignor, Consignee)। Improved scorer GT-band y-নিয়ম ব্যবহার করে — GT স্বাধীন ground truth, তাই improved-ই সঠিক মাপ: **৮১/৮১**।
- **GT সংশোধন (গুরুত্বপূর্ণ):** কাজ দেওয়া GT পথটি পুরোনো ছিল (L10/L13 span ভুল, ৪৯/৮১); সঠিক ভিত্তি Round 9 মার্জ-সংশোধিত GT (`merge-1089/n5-ground-truth-r9m.json`, ৫৭/৮১)।
- **দশমিক ভাঙন:** p2 — ৪টি সংখ্যা (NET.WT. 10138.43KGS, Bottom 58802.89, N5 11459.00KGS, GROSS.WT.) এখন ১ বাক্স। p3 — **১২টি সংখ্যা (১৩ মার্জ)**, R5-র হাতে গোনার চেয়ে ৩টি বেশি (desc 10138.43, FOB 56775.2, freight-লাইন 58802.89 — R5 মিস/ভুল গুনেছিল)। **০ false merge**; ৪টি ভুল মার্জ প্রস্তাব চোখে বাতিল (NET./WEIGHT, GROSS./WEIGHT, NO./1-013,, BENAPOLE-কমা — dot-bridge জ্যামিতি দিয়ে দশমিক বিন্দু আর সংক্ষেপণ-বিন্দু/কমা আলাদা করতে পারে না)।
- **Raviraj পূর্ণ-পাতা: ৫৬০/৭৯৫ (৭০.৪%) → ৫৯১/৭৯৫ (৭৪.৩%)** strict; improved ৫৬৩ → **৫৯৫/৭৯৫ (৭৪.৮%)**। p2 ৩০৪→৩২৬, p3 ২৫৬→২৬৫।
- **PG regression নেই:** sample ৫১৮/৫১৮, fontfix ৪৩/৪৩, title ১৪/১৪, H2 ১৪/১৪ — সব ধরে আছে; PG seg অপরিবর্তিত।
- **p3 প্রয়োগ-ঘটনা:** প্রথম apply-তে ২টি অনুমোদিত মার্জ বাদ পড়ে (signature mismatch — E অপারেশনের পরে তৈরি signature অনুমোদিত নয়)। ২টি prerequisite E অপ যোগ করে আবার চালানো: **১৫/১৫ প্রয়োগ, ০ বাদ-পড়া-অনুমোদিত, ০ অননুমোদিত-প্রয়োগ**। ১২টি p3 মার্জ-বাক্স যাচাইকৃত, পুরোনো টুকরো নেই।
- **খোলা:** p3-র span-স্তরের GT নেই (এর +৯ R5-র হাতে গোনার ওপর দাঁড়িয়ে); rule D-র জ্যামিতি-সীমা; strict scorer-এর median-y নিয়ম ৪টি সঠিক বাক্স কম গোনে (improved scorer-ই ঠিক, দুটো সংখ্যাই রিপোর্ট করা হয়েছে)।

## ৩. Track B — H1 মার্জ-দৃঢ় + May WIDTH bold (সম্পূর্ণ)

### ৩.১ H1 সরু সমাধান অসম্ভব — প্রমাণিত
- ১৪টি PG পাতায় r8m→r9m একমাত্র H1 পার্থক্য Aug p2 লাইন ৩ (bar_ink ০.১৭৬ → ০.১২৫); মার্জ gap সংকেতও ভাঙে (gap_ink ০.৩১০ → ০.০৭৬); band frame-এ bar-প্রমাণ নেই (edge_ink ০.০০৮)।
- নতুন আবিষ্কার: Aug E-mail/Website হেডার লাইন ৮টি Aug পাতায় **একই ভৌত লাইন** (৩× চোখে দেখা — একই bold লেখা ও dithered wash), কিন্তু বর্তমান নিয়ম মাত্র ২ পাতায় flag করে (bar_ink ০.১০৭–০.১৭৬) — r8m "সত্য" threshold-ভাগ্য।
- নিখুঁত খোঁজ (monotone যুক্তি, ১০ সংকেত): ০টি এক-সংকেত arm; ১৩টি দুই-সংকেত arm শুধু ≤০.০১০ ফাঁকে "কাজ করে"; ৭৮টি তিন-সংকেত arm একইভাবে; সংবেদনশীলতা সব মেরে ফেলে: **±১px band shift-এ ০/১৩ ও ০/৭৮ টেকে** (±৫ Otsu: ১/১৩ ও ২/৭৮)। সরু সমাধান overfitting হতো — নেওয়া হয়নি; Round 9 §৫.৩ override ডকুমেন্টেড থাকে (মার্জে সরানো হয়েছে, §৫ দেখুন)।

### ৩.২ যাচাইকৃত বিকল্প (B) — আসল নিয়ম-সংশোধন, মার্জে গৃহীত
- **নিয়ম:** H1 iff `band_grey < 220` OR `bar_ink > 0.15` OR (`gap_dark ≥ 0.155` AND `bar_ink ≥ 0.072`)। gap_dark = inter-word gap pixel-এ grey < ২৩৫-এর ভগ্নাংশ (halftone dither; কাগজ ~২৪৯)।
- **মার্জিন (r9m, দুই seg family):** gap_dark হেডার সর্বনিম্ন ০.১৯৫ বনাম অ-হেডার সর্বোচ্চ ০.১১৬ (gap +০.০৭৯); bar_ink হেডার সর্বনিম্ন ০.১০৭ বনাম অ-হেডার সর্বোচ্চ ০.০৩৭ (gap +০.০৭০)। দুটোই ০.০১০ knife-edge-এর ৭–৮ গুণ।
- **মার্জের নিজের re-run (shared heading.py, r9m):** TITLE **১৪/১৪**, H2 **১৪/১৪**, H1-diff **০** — r9m ও r8m দুই family-তেই।
- **খরচ:** Aug p1 live পাতায় ৩টি শব্দ regular→bold ([970,418,1061,450] ratio ০.১২০, [1123,418,1271,450] ratio ০.১১৪, মার্জ-করা www বাক্স [1459,420,1719,457] ratio ০.১০৪); Aug p2-তে ০ (আগে override-এ ছিল); May-তে ০। H2 অপরিবর্তিত।
- **(B) shared `heading.py`-তে প্রয়োগ করা হয়েছে** (GAP_DARK_THR ০.১৫৫, GAP_BAR_THR ০.০৭২, diag-এ gap_dark যোগ)।

### ৩.৩ May WIDTH প্রত্যাশা BOLD-এ পরিবর্তন — সম্পূর্ণ (সিদ্ধান্ত: parent, blanket permission-এ)
- May-র ৩ পাতা staging-এ পুনর্নির্মিত (r9m seg, WIDTH identity-box override; কোনো threshold নড়ানো হয়নি)। WORDS diff সার্জিক্যাল: May p1 ঠিক ১ entry (bold False→True, ৪৪→৪৫ bold), May p2 ঠিক ১ entry (৪৪→৪৫), May p3 ০ entry — byte-identical পাতা।
- Verifier প্রত্যাশা শুধু r10b কপিতে বদলানো (canonical অপরিবর্তিত ছিল): fontfix_verify300_r10b ও verify_may23_pages_r10b-তে May WIDTH obs bold 700; Aug WIDTH regular 400 অপরিবর্তিত; check-count অপরিবর্তিত ৪৩। Control প্রথমে: নতুন verifier বনাম root পাতা ঠিক বদলানো check-গুলোতেই fail করে (fontfix ৪২/৪৩, may23 ৪২/৪৩)। Staging-এ: **fontfix ৪৩/৪৩, May p2/p3 ৪৩/৪৩** (আগে ৪২/৪৩)।
- পূর্ণ re-run সবুজ: verify_round2 ১৮/১৮, manual ১০/১০, identity ১৫/১৫, repro PASS, save→label ৯০/৯০, sample ৫১৮/৫১৮, title/H2 ১৪/১৪, শেয়ার্ড DB SHA 1c065457… অপরিবর্তিত।
- **চোখে দেখা:** bold "671.5"/"721.5" ক্লিপ (সঠিক row, Hard অক্ষত, doubling নেই) ও save-label স্ক্রিনশট।
- **সতর্কতা:** typed width ratio ০.৯৬/০.৯১/০.৯২; long-replacement "1234.56" ১.০৯/১.০৮/১.০৯, fs-ratio ০.৬৬–০.৬৭ — পাস কিন্তু ০.৬০ clamp floor-এর কাছাকাছি (flag করা হয়েছে)।
- **মার্জের জন্য প্রশ্ন ছিল:** (১) H1 নিয়ম (B) নেওয়া হবে কি override থাকবে — **(B) নেওয়া হয়েছে** (§৫); (২) ৩টি staging May পাতা promote + canonical verifier diff — **করা হয়েছে** (§৬); (৩) write-back edit-state bold প্রশ্ন — **সমাধান করা হয়েছে** (§৭)।

## ৪. Track C — Description + www.pgfoils.in + write-back পুনর্নির্মাণ (সম্পূর্ণ)

### ৪.১ Description: ৬৩/৬৯ → ৬৯/৬৯ (০ error) — বড় আবিষ্কার
- "QUANTITY inner split" বলে কিছু নেই — x670–678-এর ৮px gap আসল word gap; mega-component [603,670] হলো "NTITY" (৫টি জোড়া অক্ষর); [678,776] "tail run" হলো পরের শব্দ 10138.43, QUANTITY-র লেজ নয়।
- **আরও বড়: R8/R9 Description GT-র L3 row এক শব্দ ডানে সরা ছিল** (R8 GT-র ভুল, R9 GT-তেও একই): GT QUANTITY [549,776] আসলে QUANTITY + 10138.43 ঢাকে; GT 10138.43 [784,840] আসলে KGS,; GT KGS, [848,903] আসলে UNIT; GT UNIT [910,966] আসলে "PRIC"; GT PRICE [967,1038] আসলে "E"+"USD"-র শুরু; GT USD [1046,1098] "USD 5.80/"-র ভেতরে; GT 5.80/KG.. [1099,1146] শুধু "KG.."। প্রমাণ: ink-run column profile, per-run glyph-stack ছবি, সবুজ/লাল overlay। r8m segmenter L3-তে বেশিরভাগ ঠিক ছিল ([549,670], [678,776], [784,834], [848,903], [910,982], [990,1038], [1046,1133]); R9 Track A ভুল GT-র সঙ্গে মিলিয়ে seg পুনর্নির্মাণ করে, আর scorer (seg বনাম GT — দুটোই একইভাবে ভুল) ৬৯/৬৯ দেখায় — **বৃত্তাকার**।
- পূর্ণ ১৪-লাইন Description audit (১০টি eye-check ক্লিপ): L1 COATED কমা judgement call ([1011,1725,1015,1733], ৪×৮px, baseline); L2 OK; L3 সরা; L4 CPT-র C বাদ পড়েছিল (আসল [549,620], GT [567,620] — C একটি তির্যক vertical bar/stamp-edge component [533,1777,565,1809]-এর সঙ্গে জোড়া; C-র বাম প্রান্ত ৫৪৯ grey-value row y=1788/1793/1798 দিয়ে মাপা) + BENAPOLE কমা ([736,1795,741,1805], চোখে নিশ্চিত) → "BENAPOLE," [621,741]; L5/L6/L7 OK (লম্বা vertical component rule/stamp প্রান্ত); L8 VALUE: colon বাদ পড়েছিল (দুটি dot [688,1882,693,1887] + [688,1891,692,1895]) → [605,693]; L9/L10 OK; L11 সংখ্যার কমা বাদ পড়েছিল ([845,1968,849,1977]) → [641,849]; H.S.CODE [856,972] OK; L11 NO./7607 neck ১০২১-এ নিশ্চিত; L12 OK; L13 REGN./NO. neck + সংখ্যার শুরু ৯২৩ নিশ্চিত (R9-র ৬× যাচাই আবার দেখা; ৯১৬–৯২২ কালি শুধু stamp speck); L14 OK।
- সংশোধিত GT + seg (১২ span সংশোধিত): control ১ — r9m seg বনাম সংশোধিত GT **৬৩/৬৯** (ভুল: L3 QUANTITY, 10138.43, PRICE, USD, 5.80/KG.. + L4 CPT) — এটাই Round 9-র আসল স্কোর, ৬৯/৬৯ নয়; control ২ — r8m seg বনাম সংশোধিত GT ৪৩/৬৯ (R9-র অন্য সংশোধনগুলো আসল ছিল: ৪৩→৬৩); control ৩ — r10 seg বনাম পুরোনো R9 GT ৬৩/৬৯ (প্রতিসম; GT ও seg একসঙ্গে সরতে হয়)।
- **N5 অপরিবর্তিত:** n5_score_r9m.py দুই seg-এই ৫৭/৮১ দেয় (একই per-line টেবিল)। N5 GT (merge-1089) শুধু desc-L06–L14 ঢাকে (L3/L4 নেই), কিন্তু একই ২টি ছোট span ভুল বহন করে (VALUE: colon, সংখ্যার কমা) — মার্জে সংশোধন করা হয়েছে (§৫.৩)।
- মোট: Raviraj p2 মোট ৩০৪/৫০২ ও পূর্ণ পাতা ৫৬০/৭৯৫ সংখ্যায় অপরিবর্তিত (Description অবদান NOT-সহ এখনো ৭০/৭০), কিন্তু এখন কালি-যাচাইকৃত GT-র ওপর দাঁড়িয়ে, বৃত্তাকার সম্মতির ওপর নয়।

### ৪.২ www.pgfoils.in — নতুন ধারণা, প্রমাণিত
- ৩ টুকরো ("www" / "pgfoils" / "in"), প্রতিটিতে দুটি period dot seg বাক্স থেকে বাদ। Aug-p2 ink-run (band y410–455, Otsu): www=(1458,1549), dot=(1553,1559), pgfoils শুরু ১৫৬৪, dot=(1679,1685), in=(1691,1718)। Dot ৬–৭px চওড়া, ink band-এর নিচের ৮ row-এ সীমাবদ্ধ (baseline) — period, অক্ষর নয় (৮× zoom চোখে নিশ্চিত)।
- **Line-local gap-split (নতুন ধারণা — R8 DNA-glyph matcher নয়):** ১৪টি PG পাতায় মাপা। Threshold ≤৬ www জোড়ে **১৪/১৪ পাতায়, ০ false merge, ০ false split** (কোনো পাতায় word-gap ≤৬ নেই; label-ভেতরের gap ১–৫, n=১৬৭; word gap ৮–১৩, n=৪২, সর্বনিম্ন ৮; www-ভেতরের gap ১–৫, সর্বোচ্চ ৫)। প্রতি পাতায় ঠিক ২টি uncovered dot run, সব baseline-low।
- Partial-exemplar সমর্থন: template = website কালি x1553–1718 e-mail বাক্সের কালির ওপর slide; Aug-p2 সেরা IoU ০.৭৩৪৯, x=1113 (সঠিক tail অবস্থান), scale ০.৯৬; margin ০.২৮১২; cross-page aug-p3 IoU ০.৭২১ @০.৯৬ / ০.৭৫৭ @০.৯৮, may-p3 ০.৬৫০ @০.৯৬ / ০.৬৯৭ @০.৯৮ / ০.৬৯৮ @১.০০। R8 gate (IoU ≥০.৬০, margin ≥০.০৫) ৩/৩ পাতায় পাস। সতর্কতা: fitted scale ০.৯৬–০.৯৮ দরকার (e-mail tail website rendering-এর চেয়ে ~২–৪% সরু — systematic); scale ১.০০-তে aug-p2/aug-p3 ০.৬০ gate-এ fail করে (০.৪৭/০.৫৫)। Exemplar সমর্থনকারী প্রমাণ; gap+dot নিয়মই মূল প্রমাণ।
- Staging seg (১৪ ফাইল): প্রতিটি ৩টি www বাক্সের বদলে ১টি মার্জ-বাক্স [x0, min-y1, x1, max-y2] (যেমন aug-p2 [1458,414,1718,450])। ১৪টি পাতায় সব যাচাই OK: word count ঠিক −২, দুটি dot-ই ঢাকা (x ও y), অন্য কোনো বাক্সের সঙ্গে overlap নেই, বাকি সব বাক্স r9m-র সঙ্গে byte-identical। মার্জ-বাক্স overlay চোখে দেখা।

### ৪.৩ Write-back পুনর্নির্মাণ (Track C staging) — ৪১/৪১
- Baseline পুনরুৎপাদন ৩৬/৪০, ৪ fail — সব ink-IoU (aug Lot ০.৩০৯, aug WIDTH ০.৪০৯, may Lot ০.৩৩১, may WIDTH ০.৪১১)। ৪০ বনাম ৪১ স্পষ্টকরণ: track-c verifier-এ ৪০ check; Round 9-র "৩৭/৪১" Round 4 track-a ধাঁচের verifier (৪১ check = ৪০ − LSE-0003 history-check + ২ supersede-check), একই ৪ IoU fail।
- পুনর্নির্মাণ: একই edit state, একই বাক্স, একই BUILD_VERSION v2.1-300dpi, একই output ফাইলের নাম; শুধু বর্তমান font/size বদলেছে। নতুন delivery LSE-0008 (aug) ও LSE-0009 (may), LSE-0006/LSE-0007-কে supersede করে — শুধু এই staging DB কপিতে (এখন ৯ delivery, ২৬ audit, SHA 56b45c9e…)। নতুন font size (full precision, সব Document DNA Regular): aug Lot ৩৩.৮৪ → ৩৭.৯১০৮৭৯১৮৩২১০৪৪ px; aug WIDTH ৩৬.৩২ → ৪০.৮৬৭৩৩৫৯০৭৩৩৫৯ px; may Lot ৩৪.০১ → ৩৭.৭৯৮৯৩০১০৪৫৬৭৯৭ px; may WIDTH ৩৬.৯২ → ৪১.১২৫ px।
- যাচাইয়ের পর: verify_rebuild_300.py (track-c, ৪০ check) **৪০/৪০, failures: none**; verify_writeback300_r10.py (merge-ধাঁচ, ৪১ check) **৪১/৪১, failures: none**। প্রতি-edit ink-IoU পরে: সব **১.০০০**। দুটি supersede check PASS। বাকি সব check PASS (background JPEG/CCITT byte-identical, patch-বাইরে pixel-diff ০, প্রতিবেশী 'Hard' অপরিবর্তিত, DB read-back + delivery_hash + PDF SHA == DB, hash chain ২৬ entry, trigger UPDATE-block, দুটি tamper test)। চোখে দেখা ৪ ক্লিপ — সব সঠিক row-তে, মূল typeface-এর সঙ্গে মিলে।
- সতর্কতা (মার্জের জন্য): Track C-র LSE-0008/LSE-0009 Round 10 Track C staging delivery — Round 4 track-a-র LSE-0008/0009 (অন্য DB ফাইল) ও মার্জের LSE-0010/0011 থেকে আলাদা — নম্বর দিয়ে মার্জ করা যাবে না।

## ৫. মার্জ সিদ্ধান্ত — H1 (B) বনাম www মার্জ সংঘাত (মার্জের নিজের কাজ)

### ৫.১ সমস্যাটি (মার্জের নিজের পরিমাপ)
Track B-র (B) নিয়ম shared heading.py-তে প্রয়োগ করে মার্জের checker (`check_titles_h2_r10m.py`, shared heading.py + r10m seg) চালানো:
- **r9m family: TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০** (r9m ও r8m দুটোতেই — Track B-র দাবি নিজে চালিয়ে নিশ্চিত)।
- **r10m family: TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ২** — **aug-p2 ও aug-p3-র লাইন ৩ (হেডার লাইন) H1 থেকে পড়ে যায়**।

কারণ (মাপা, অনুমান নয়): www মার্জ লাইন ৩-র gap সেট বদলে দেয়। aug-p2: gap_dark ০.২২৫ → **০.১৪৮** (threshold ০.১৫৫-র নিচে, মাত্র ০.০০৭ কম); aug-p3: gap_dark ০.১৯৫ → **০.০৯৭**। bar_ink উল্টো বেড়েছে (p2: ০.১২৫→০.১৪২, p3: ০.১০৭→০.১২১)। বাকি ৬ Aug পাতায় gap_dark বেড়েছে (০.৫০৫–০.৫৬০) — p2/p3-র www-ভেতরের gap-গুলোই সবচেয়ে অন্ধকার ছিল, সেগুলো সরতেই ভগ্নাংশ পড়ে গেছে।

### ৫.২ কোনো threshold-ই r10m-এ হেডার আলাদা করতে পারে না (সব মাপা)
৫৬১ লাইনের পূর্ণ diagnostic (r10m):
- **band_grey:** হেডার সর্বোচ্চ ২৩৭.২; অ-হেডার অ-H1 সর্বনিম্ন ২৩০.৮ (aug-p2 L6) — হেডারের চেয়ে অন্ধকার। আলাদা করে না।
- **bar_ink:** হেডার সর্বনিম্ন ০.১২১ (aug-p3); অ-হেডার সর্বোচ্চ ০.১৩৬ (may-p5 L3) — overlap। আলাদা করে না।
- **gap_dark:** হেডার সর্বনিম্ন ০.০৯৭; অ-হেডার সর্বোচ্চ ০.২৫১ (aug-p7 L36) — overlap। আলাদা করে না।
- **wash (band-স্তর):** wash200 হেডার ০.২৬২–০.৩৩০, অ-হেডার সর্বোচ্চ ০.৪৯৪ (aug-p2 L23 — table এলাকা); wash180, dark fraction, mean_all — কোনোটাই আলাদা করে না।
- **দ্বিমাত্রিক:** (bar ≥ ০.১০ AND gap ≥ ০.০৮) may-p4 L4-কে ভুলে H1 বানায় (০.১৩২, ০.০৮১); (bar+gap ≥ X) aug-p7 L36-কে ভুলে নেয় (যোগফল ০.২৮৮ > aug-p3-র ০.২১৮); (bar ≥ ০.১২ AND gap ≥ ০.০৯) aug-p3-তে মাত্র ০.০০৭ মার্জিন — knife-edge, overfitting। **সব বাতিল।**

### ৫.৩ মার্জের সিদ্ধান্ত — heading r9m seg থেকে, (B) গৃহীত, override সরানো
- **(B) নিয়ম গৃহীত** — shared heading.py-তে আছে, r9m-এ দুই family-তেই যাচাইকৃত (TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০)।
- **www মার্জ গৃহীত** — r10m seg, যাচাইকৃত (প্রতি পাতায় ঠিক ৩→১, ০ false merge)।
- **heading হিসাব r9m seg থেকে:** heading লাইন-স্তরের বৈশিষ্ট্য; লাইন-গঠন দুই seg-এ অভিন্ন (H2 ১৪ পাতায় একই; H1 একই — শুধু aug-p2/p3 L3, www-মার্জ artefact)। মার্জের নিজের তুলনা (shared heading.py, দুই family): r9m বনাম r10m H1 সেট — **শুধু aug-p2/p3 L3-তেই পার্থক্য**। তাই live পাতার builder-গুলো শব্দ r10m seg থেকে নেয়, heading (H1/H2 লাইন সেট) r9m seg থেকে হিসাব করে।
- এটা Round 9 §৫.৩-র মতো হার্ডকোড লাইন override **নয়** — H1 সেট আসল (B) নিয়ম দিয়ে document image থেকে হিসাব করা হয়; শুধু heading হিসাবের জন্য seg সংস্করণটি যাচাইকৃতটিতে pin করা। **§৫.৩ override (`_h1 | {3}`) Aug p2 builder থেকে সরানো হয়েছে।**
- **চোখে যাচাই:** Aug p1 ও p2 হেডার লাইন ২× zoom-এ — দুটি পাতায় অভিন্ন bold লেখা ("EMAIL: pgfoils@pgfoils.in WEBSITE: www.pgfoils.in"), একই dithered wash। ৩টি flip-শব্দই এই bold লাইনের অংশ।
- **খোলা গবেষণা-সমস্যা:** merge-invariant gap_dark (যা seg-মার্জে বদলায় না) এখনো নেই — ভবিষ্যৎ রাউন্ডের কাজ।

### ৫.৪ Raviraj p2 seg মার্জ — Track A বনাম Track C সংঘাত নেই
- Box-set তুলনা: A-added ∩ C-added = ০, A-added ∩ C-removed = ০, C-added ∩ A-removed = ০, A-removed ∩ C-removed = ০ — **দুটি ট্র্যাক সম্পূর্ণ আলাদা বাক্স বদলেছে**। r10m Rav p2 = r9m + A-diff + C-diff, ৫৯৯ শব্দ, merged box set == প্রত্যাশিত union (assert দিয়ে যাচাইকৃত)।
- L3-তে একটি পুরোনো বাক্স [549,776] দুটি নতুন বাক্সে ভাগ হয়েছে ([549,670] + [678,776]) — partner-matching-এ IoU ০.৪৩২, লাইন None (Description জোনে সব None; Raviraj seg scoring-only)।
- **N5 GT-র ২টি span ভুল সংশোধন (Track C-র কালি-প্রমাণ অনুযায়ী):** desc-L08 VALUE: [605,686] → **[605,693]** (colon dot); desc-L11 সংখ্যা [641,846] → **[641,849]** (কমা)। সংশোধিত GT-তে N5 improved **৮১/৮১**, strict **৭৭/৮১**; r9m baseline সংশোধিত GT-তেও ৬০/৮১ (GT বদলে baseline ফোলেনি); Track A r10a seg সংশোধিত GT-তেও ৮১/৮১।

### ৫.৫ May WIDTH bold — মার্জে promote
- ৩টি May পাতা r10m seg + bold WIDTH override দিয়ে পুনর্নির্মিত; canonical verifier diff প্রয়োগ করা হয়েছে (fontfix_verify300 + verify_may23_pages: May WIDTH obs bold 700; Aug regular 400 অপরিবর্তিত)।
- May p1 WIDTH ratio ০.১৫৫ বনাম threshold ০.১৫৪ (মাত্র ০.০০১ মার্জিনে ratio-তেই bold — override খালি); May p2 ratio ০.১৪৯ < ০.১৫৫ — **override fire করেছে**; May p3 ratio ০.১৫৬ বনাম ০.১৫৫ (০.০০১ মার্জিনে ratio-তেই bold)। ফলাফল (bold) দৃঢ় — ratio বদলালে identity-box override ধরে ফেলবে; শুধু mechanism বদলায়।

## ৬. মার্জে যা বদলেছে (promote করা হয়েছে)

**Live পাতা (root, ৫টি — সব নতুন SHA):**
| পাতা | আগে (R9) | **এখন (R10)** | শব্দ | bold |
|---|---|---|---|---|
| Aug p1 | 047a6d6b… | **1ed03550…** | ৩০২ | ৭৭ |
| Aug p2 | 3dbab180… | **ddedc569…** | ২৯৭ | ৭০ |
| May p1 | 8944d835… | **9abc7a81…** | ৩০২ | ৪৩ |
| May p2 | 82ab16d0… | **c212b72a…** | ৩০৩ | ৪৩ |
| May p3 | db72deaa… | **8ca8d5cb…** | ৩০১ | ৪৫ |

**Seg (canonical):** root `seg-aug-p1-300.json` ও `seg-may-p1-300.json` r10m-এ আপডেট (৩০২ শব্দ); `improve/round4/merge/segs/seg-may-p2-300m.json` (৩০৩) ও `seg-may-p3-300m.json` (৩০১) r10m-এ আপডেট। r10m family `improve/round10/merge-r10/segs/`-এ (১৪ PG + Rav p2/p3 + সংশোধিত N5 GT)।
**Clean:** ৫টি live পাতার clean inpaint.py দিয়ে r10m seg-এ পুনর্নির্মিত (`merge-r10/cleans/`)। www dot যাচাই: পুরোনো clean-এ dot-এ ২২/২০ dark px ছিল (মুছে যায়নি), নতুন clean-এ **০** (paper grey ২৪৩.৬/২৪৩.৫)। বাকি পার্থক্য শুধু grain noise পুনরায় আঁকা (mean diff ০.৫৬/২৫৫, অদৃশ্য; blank margin byte-identical ০.০)।
**Verifier (canonical):** fontfix_verify300.py (৩০৪→৩০২ ×২, May WIDTH bold), verify_round2_300.py (৩০৪→৩০২ ×২), verify_may23_pages.py (May WIDTH bold, ৩০৫→৩০৩ / ৩০৩→৩০১)। পুরোনো root পাতা + verifier `merge-r10/backup/`-এ।
**Edit-state (canonical):** `improve/round3/track-c/lse-edit-state-may.json`-এ May WIDTH bold false → **true**।
**Heading:** shared `heading.py`-তে (B) arm (GAP_DARK_THR ০.১৫৫, GAP_BAR_THR ০.০৭২)। Root heading JSON অপরিবর্তিত — (B) নিয়ম Round 9-র H1 সেট হুবহু পুনরুৎপাদন করে (Aug p2-সহ)।

## ৭. চূড়ান্ত যাচাই টেবিল (মার্জের নিজের re-run — সব সংখ্যা এই রাউন্ডে চালিয়ে মাপা)

| যাচাই | ফল (Round 10 মার্জ) | Round 9 |
|---|---|---|
| fontfix_verify300 (canonical) | **৪৩/৪৩** | 43/43 |
| verify_round2_300 (canonical) | **১৮/১৮** | 18/18 |
| repro300 (doubling) | **PASS** | PASS |
| manual_proof300 | **১০/১০** | 10/10 |
| Identity probe (Lot+WIDTH+Hard, ৫টি live পাতা) | **১৫/১৫** (চোখে দেখা — Lot পরিষ্কার, WIDTH পরিষ্কার, "Hard" অক্ষত, doubling নেই) | 15/15 |
| Write-back (মার্জ, ৪১-check) | **৪১/৪১, FAILURES: none** | 41/41 |
| Write-back (পুনর্নির্মাণ, ৪০-check) | **৪০/৪০, FAILURES: none** (May WIDTH bold font-এ ink IoU ১.০০০) | — |
| Write-back (Round 3 পুরোনো v1 staging, ৩৩-check) | **২৯/৩৩** — একই ৪ known ink-IoU fail (Aug ০.৩০৯/০.৩৭২, May ০.২৮০/০.৪৪৬); supersede-করা artifact, regression নয় | 37/41 (৪১-check ধাঁচে) |
| Track D staging | **৪৮/৪৮** | 48/48 |
| Track C staging (R5) | **৭৪/৭৪** | 74/74 |
| May multipage | **৫৯/৫৯** | 59/59 |
| May p2/p3 | **৪৩/৪৩** — knife-edge সমাধান | 42/43 |
| sqlcipher | **১৫/১৫** | 15/15 |
| keymgmt | **২৫/২৫** | 25/25 |
| Save→label live (৫ পাতা) | **৯০/৯০** | 90/90 |
| Aug p2 live পাতা (r10m) | **১৬/১৬** (root পাতায় চালানো) | 16/16 |
| PG sample (r10m seg) | **৫১৮/৫১৮, অতিরিক্ত ০**; টাইটেল ১৪/১৪, H2 ১৪/১৪ | 518/518 |
| H1 (B) নিয়ম (r9m, দুই family) | **TITLE ১৪/১৪, H2 ১৪/১৪, H1-diff ০** | — |
| H1 (B) নিয়ম (r10m) | **H1-diff ২** (aug-p2/p3 L3 — www-মার্জ artefact, §৫; live পাতায় r9m heading ব্যবহারে সমাধান) | — |
| Description (r10m seg, সংশোধিত GT) | **৬৯/৬৯, ০ error** | 69/69 (বৃত্তাকার GT-তে) |
| N5 (r10m seg, সংশোধিত GT) | **৮১/৮১** improved; strict ৭৭/৮১ | 57/81 |
| Raviraj পূর্ণ-পাতা (r10m) | **৫৯১/৭৯৫ = ৭৪.৩%** strict; ৫৯৫/৭৯৫ = ৭৪.৮% improved (p2 ৩২৬/৫০২, p3 ২৬৫/২৯৩) | 560/795 = 70.4% |
| শেয়ার্ড DB (read-only যাচাই) | **SHA 1c065457…, ৭ delivery, ২০ audit entry — অপরিবর্তিত** | একই |

**মার্জ staging DB** (নতুন copy, শেয়ার্ড DB নয়): ৯ delivery, ২৬ audit entry; মার্জের LSE-0008 (aug, PDF 17e7f793…) ও LSE-0009 (may, PDF fe29d599…) LSE-0006/LSE-0007-কে supersede করে। May WIDTH bold:true-তে render করা (fs ৪১.১২৫ px, ink IoU ১.০০০, inter ১২৯৬/union ১২৯৬)। Aug WIDTH fs ৪০.৮৬৭৩৩৫৯০৭৩৩৫৯১, Lot ৩৭.৯১০৮৭৯১৮৩২১০৪৪।

**চোখে দেখা (সব):** ৫টি live পাতার full-page স্ক্রিনশট (Lot + WIDTH পরিষ্কার, "Hard" অক্ষত, doubling নেই; May-র ৩ পাতায় WIDTH DNA Bold-এ render — font প্যানেলে সবুজ highlight); Aug p1/p2 হেডার লাইন ২× zoom-এ অভিন্ন bold; write-back PDF ক্লিপ ৪টি (May "671.5" bold, Aug "781.5" — দুটোই সঠিক row-তে, "Hard"-এর নিচে); www dot মুছে যাওয়া (পুরোনো clean ২২/২০ dark px → নতুন clean ০)।

## ৮. সৎ সীমা — এখনো যা সম্পূর্ণ নয়

1. **Merge-invariant gap_dark নেই।** (B) নিয়ম r9m-এ যাচাইকৃত, কিন্তু www-মার্জের মতো seg-বদলে gap সেট বদলে যায় — r10m-এ aug-p2/p3 হেডার পড়ে যায়। বর্তমান সমাধান (heading r9m seg থেকে) সঠিক ও ডকুমেন্টেড, কিন্তু seg-স্বাধীন সংকেত এখনো গবেষণা-সমস্যা।
2. **May WIDTH bold knife-edge (ratio-তে)।** May p1 (০.১৫৫ বনাম ০.১৫৪) ও p3 (০.১৫৬ বনাম ০.১৫৫) ratio-তে মাত্র ০.০০১ মার্জিনে bold। ফলাফল দৃঢ় (identity-box override safety net), কিন্তু median-এর সামান্য নড়াচড়ায় mechanism বদলাবে।
3. **May long-replacement মার্জিন সরু।** "1234.56" width ratio ১.০৯, fs-ratio ০.৬৬–০.৬৭ — পাস, কিন্তু ০.৬০ clamp floor-এর কাছাকাছি (Track B-র flag)।
4. **Raviraj ৭৪.৩% (৫৯১/৭৯৫)।** দশমিক ভাঙন ঠিক হয়েছে (+৩১), কিন্তু p2 ৩২৬/৫০২ = ৬৪.৯% — বাকি ভুলগুলো (decimal-বাইরে) এখনো ঠিক হয়নি। p3-র +৯ R5-র হাতে গোনার ওপর দাঁড়িয়ে (span-স্তরের GT নেই; আসল লাভ +১২ পর্যন্ত হতে পারে — Track A §৪.৩)।
5. **Rule D জ্যামিতি-সীমা:** dot-bridge দিয়ে দশমিক বিন্দু বনাম সংক্ষেপণ-বিন্দু/কমা আলাদা করা যায় না (৪টি ভুল মার্জ প্রস্তাব চোখে বাতিল)।
6. **Strict scorer-এর median-y নিয়ম** ৪টি সঠিক বাক্স কম গোনে (Reg., pay, Consignor, Consignee) — improved scorer-ই সঠিক মাপ; দুটো সংখ্যাই রিপোর্ট করা হয়েছে।
7. **আগের মতোই খোলা:** print calibration (factory printer), US patent আইনি যাচাই (উকিলের কাজ), DBNet swap deferred, DPAPI প্রমাণ VM-এ হয়নি, `raviraj COA 20 micron.jpg` workspace-এ পাওয়া যায়নি, অন্য ২৫ PDF পাতা শুধু contact-sheet দেখা (~৮০০০ শব্দ, হাতে গোনা হয়নি)।
8. **মার্জ staging নম্বর-সতর্কতা:** মার্জের LSE-0008/LSE-0009 Track C-র staging LSE-0008/LSE-0009-এর সঙ্গে একই নম্বর কিন্তু **আলাদা DB ফাইল** — নম্বর দিয়ে মেলানো যাবে না। শেয়ার্ড DB অপরিবর্তিত (LSE-0001–0007)।
9. **Track C-র পুরোনো v1 staging PDF** এখনো ৪টি ink-IoU fail দেখায় (২৯/৩৩) — এটা pre-fix artifact; পুনর্নির্মিত artifact ৪১/৪১। পুরোনো ফাইলগুলো archive-এ আছে, মুছে ফেলা হয়নি।

## ৯. ফাইল (মার্জ ডিরেক্টরি)

- `improve/round10/merge-r10/ROUND10-REPORT.md` — এই রিপোর্ট (মার্জ ডিরেক্টরির বাইরে `improve/ROUND10-REPORT.md`-এও রাখা হয়েছে)।
- `improve/round10/merge-r10/segs/` — r10m family (১৪ PG + Rav p2/p3 + সংশোধিত N5 GT)।
- `improve/round10/merge-r10/pages/` — ৫টি পুনর্নির্মিত live পাতা (root-এ promote করা হয়েছে)।
- `improve/round10/merge-r10/cleans/` — ৫টি পুনর্নির্মিত clean (+ ৫টি manual clean কপি)।
- `improve/round10/merge-r10/scripts/` — seg assembly, builder patch, builder (৪টি), scorer (N5 strict/improved, Description), checker (title/H2 r10m), probe_identity_r10m, sample_rows_r10m।
- `improve/round10/merge-r10/verifiers/` — fontfix_verify300_r10m, verify_may23_pages_r10m, verify_aug2_page_r10m।
- `improve/round10/merge-r10/writeback/` — মার্জ staging DB (৯ delivery, ২৬ audit) + v2.1 PDF + ৪০/৪১-check verifier।
- `improve/round10/merge-r10/backup/` — promote-আগের ৫টি পাতা + root verifier কপি (SHA যাচাইকৃত)।
- `improve/round10/merge-r10/clips/` — identity probe ক্লিপ + eye-check full-page স্ক্রিনশট (৫টি) + H1 হেডার ক্লিপ (২টি)।
- `improve/round10/merge-r10/h1_diag_r10m.json`, `h1_wash_r10m.json` — ৫৬১ লাইনের diagnostic (সব সংকেতের separation-বিশ্লেষণ)।
- **কোনো Drive upload করা হয়নি।** REPORT.md, REPORT-MAY.md, ROUND2–9-REPORT.md অপরিবর্তিত। শেয়ার্ড Round 3 DB শুধু read-only যাচাই করা হয়েছে।
