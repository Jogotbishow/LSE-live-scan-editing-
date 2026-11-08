# Live-Scan Round 2 — চূড়ান্ত রিপোর্ট (ধাপ ১০: Consolidation)

**তারিখ:** ২০২৬-১১-০৬ · **পাতা:** PG Foils supplier COA — August (রঙিন) ও May (B&W) · **স্থিতি: সম্পূর্ণ**
**প্রযুক্তির নাম: LSE — Live-Scan Editing** (ব্যবহারকারীর সিদ্ধান্ত, ২০২৬-১১-০৬)
**ফাইল:** `scan-paper/improve/ROUND2-REPORT.md` · **সূত্র:** `improve/round2/`-এর ধাপ-রিপোর্টগুলো + ধাপ ১০-এ নিজে চালানো যাচাই

## ০. এক লাইনে

Round 2-এর ১০ ধাপের সবটাই মাপা হয়েছে, আর ধাপ ১০-এ (এই রিপোর্ট) পুরো যাচাই-স্যুটটি **নিজে আবার চালিয়ে** নিশ্চিত করা হয়েছে: **verify_round2.py ১৮/১৮ PASS, fontfix-verify.py ৩১/৩৫ PASS (৪টি ফেইল আগের থেকেই জানা সীমা), repro.py PASS, manual_proof.py ১০/১০ PASS** — কোনো ফেইল বা রিগ্রেশন নেই। Live-Scan এখন: lossless ব্যাকগ্রাউন্ড + নিখুঁত মাস্ক + Grain v2 + Document DNA (vtracer, ৬০০ DPI) ডিফল্ট ফন্ট হিসেবে — দুই পাতাতেই ডেমো এডিট সঠিক শব্দে, সঠিক জায়গায়, doubling ছাড়া।

> ⚠️ **আইনি দাবিত্যাগ:** এই রিপোর্ট কারিগরি গবেষণা, আইনি পরামর্শ নয়। লাইসেন্স/পেটেন্টের অংশ (§৬) পড়ে কোনো সিদ্ধান্ত নেওয়ার আগে একজন আইনজীবীর সঙ্গে পরামর্শ বাধ্যতামূলক।

---

## ১. ধাপ-ভিত্তিক before / after (সব সংখ্যা মাপা)

### ধাপ ১ — Lossless background (ধাপ ১–২ রিপোর্ট)
| বিষয় | আগে | পরে |
|---|---|---|
| August ব্যাকগ্রাউন্ড | JPEG q88 পুনঃ-এনকোড (চোখে এক, byte-এ নয়) | PDF-এর ভেতরের মূল JPEG byte-ই (৫১৯,৯১৬ B, SHA-256 `7b171751fb6ab757…`) |
| May ব্যাকগ্রাউন্ড | JPEG q88 পুনঃ-এনকোড | CCITT raw (৫৩,৮৭১ B) → PNG lossless ডিকোড (৭৮,১১৪ B), **৮,৬০২,৬২১ পিক্সেলের মধ্যে ০টি ভিন্ন** |
| ছবির ঘূর্ণন | জানা ছিল না | দুই PDF-ই ছবি ১৮০° ঘোরানো অবস্থায় রাখে (image matrix) — CSS `rotate(180deg)` (pixel permutation, নির্ভুল) |
| jpegtran lossless rotation | — | **প্রত্যাখ্যাত** — ছবি (−৩,−১৩) px সরে যায় (২৪৮৩×৩৪৮৫, ১৬×১৬ MCU-র গুণিতক নয়) |
| পাতার আকার | — | August +১৩.৩% (clean q95-এর খরচ), May −৫১.২% |

### ধাপ ২ — Mask-design fix (inpaint.py v3)
| বিষয় | আগে | পরে |
|---|---|---|
| টাইটেলের ধূসর বার | inpainting-এ মুছে যেত (ghost) | বার আলাদা element হিসেবে ধরা হয় — August (৬৭৮,৪০৩,৯৭৯,৪৩৮), May (৬৭১,৩৯০,৯৭০,৪২২) |
| টাইটেলের আন্ডারলাইন | বারসহ মুছে যেত | আলাদা element হিসেবে আবার আঁকা হয় — August সারি ৪৩২–৪৩৪, ৬৪৯ px; May সারি ৪১৭–৪২১, ১,০৮২ px |
| টাইটেল ghost | August ২,৭২৬ · May ৩,৫২১ | **০ · ০** |
| ব্যান্ডের গড় ধূসর | — | August ২৪৭.৮ বনাম কাগজ ২৪৭.৭; May ২৫৪.৮ বনাম ২৫৫.০ |

এই ধাপে ধরা পড়া দুটি বাগ (দুটোই ঠিক করা হয়েছে): (১) August `?demo=1` auto-run লাইন build_page.py টেমপ্লেটে হারিয়ে গিয়েছিল (v4 rebuild-এ); (২) repro.py-র WIDTH টার্গেট পুরনো ভুল `near(1420, 822)` ছিল → `near(1420, 863)`-এ ঠিক করা হয়েছে।

### ধাপ ৩ — DBNet spike (det-only ONNX) — **GO, শর্তসহ — কিন্তু primary হয়নি**
| বিষয় | মাপা ফল |
|---|---|
| গতি | warm steady-state ~১.০–১.৪ s/পাতা (মানদণ্ড: < ~২ s/পাতা) |
| Spike-এর রায় | **GO — DBNet primary detector হবে, ৪টি শর্তসহ** (C4: May-এর title fragmentation ঠিক না হওয়া পর্যন্ত classical validator হিসেবে থাকবে) |
| Integration-এ যা হলো | merged আউটপুট খারাপ হলো — August নমুনা ৩৭/৩৭ → **৩৪/৩৭**, Lot বাক্স IoU ০.৪৯, May +৩১ over-split (৩১০ বনাম ২৭৯), title-এ ১৯টি খণ্ড |
| **সিদ্ধান্ত** | **classical-ই primary থাকে** — DBNet parallel pipeline + confidence validator হিসেবে থাকে। Spike-এর GO আর integration-এর সিদ্ধান্তে বিরোধ নেই: C4 শর্তটি পূরণ হয়নি, তাই swap স্থগিত, প্রত্যাখ্যাত নয় |
| বাড়তি সুবিধা (মাপা) | DBNet এমন আসল শব্দ খুঁজে পায় যা classical মিস করেছিল — `PREM GROUP` হেডার (দুই পাতাতেই) |
| যা মাপা হয়নি | আসল ল্যাপটপে (i5-8265U) DBNet-এর সময় — এই VM-এর সময় নয় |

### ধাপ ৪ — MI-GAN spike — **NO-GO, Telea-ই থাকে**
| বিষয় | মাপা ফল |
|---|---|
| লাইসেন্স | code MIT + weights MIT — repo থেকে **VERIFIED** |
| ফেইলিওর মোড | Places2-এ train করা neural inpainter কাগজের ওপর **আবার টেক্সট বানিয়ে ফেলে** — ৫টি crop-এর সবকটিতে ghost text; C1 ব্যান্ড ১৬৯ → ১০,০৩৭ |
| রায় | **NO-GO — MI-GAN নেওয়া হয়নি, hard-spot engine হিসেবেও নয়** |
| LaMa | **নেওয়া হয়নি — কোনো spike নয়, কোনো download নয়** (MI-GAN-ই shared Places2 ফেইলিওর মোডটি প্রমাণ করে দিয়েছে) |

### ধাপ ৫ — Deskew + confidence UI
| বিষয় | আগে | পরে |
|---|---|---|
| Deskew (মাপা কোণ) | — | August +০.২৬°, May +০.১১° |
| নীতি | — | threshold **০.৫°** — May-এর ছোট কোণ ঠিক করতে গেলে নমুনা **৩৩/৩৭ → ৩১/৩৭** খারাপ হয়, তাই ছোট কোণ **রিপোর্ট করা হয়, ঘোরানো হয় না** |
| Confidence UI | শতাংশের দাবি নেই | **৩-স্তর** (শতাংশ নয়), দুই detector-এর সম্মতি থেকে — August ২৬৪/১৫/১৪, May ২৪৬/২৩/১০ |
| DBNet integration | — | তৈরি ও মাপা হয়েছে, কিন্তু swap করা হয়নি (ধাপ ৩ দেখুন) |

### ধাপ ৬ — Grain v2 (inpaint.py v4) — **LaMa নয়**
| বিষয় | আগে | পরে |
|---|---|---|
| Clean-এর grain | Telea v3, grain মেলে না | **Grain v2 নেওয়া হয়েছে** — C1 σ ৩.৮৮ → **৬.২৮** (কাগজ ৭.৫৪), ghost এখনও **০** |
| প্রথম রান | — | সৎভাবে ফেইল করেছিল — টেক্সট-কিনারার ধূসর পিক্সেল σ ~২× বাড়িয়ে দিয়েছিল; কারণ ধরা পড়ে ঠিক করা হয়েছে |
| LaMa | — | **নেওয়া হয়নি, কোনো spike নয়, কোনো download নয়** |

### ধাপ ৭ — Matcher + font shortlist
| বিষয় | মাপা ফল |
|---|---|
| Matcher | DNA clone **পাতা-স্তরে দুই পাতাতেই ১ম**, ৪টি title শব্দের সবকটিতেই ১ম — কিন্তু **সংখ্যায় নয়** (Lot/WIDTH-এ Liberation Sans Bold জেতে) |
| Font shortlist UI | দুই পাতাতেই **লাইভ** |
| বাগ | preview-refresh বাগ ধরা পড়ে ঠিক করা হয়েছে |

### ধাপ ৮ — Manual-box + stamp + print procedure
| বিষয় | মাপা ফল |
|---|---|
| Manual-box mode | **১০/১০ PASS** — চোখে ধরা পড়া আসল বাগ ঠিক করা হয়েছে (half-size backgroundSize-এর কারণে টাইপ করা টেক্সটের নিচ দিয়ে signature বেরিয়ে আসত) |
| Stamp detector | দুই পাতাতেই **কোনো stamp পাওয়া যায়নি**; mechanism ইনজেক্ট করা নকল stamp দিয়ে পরীক্ষা করা হয়েছে |
| প্রিন্টার | এই VM-এ **কোনো প্রিন্টার নেই** (যাচাই করা, ভান করা হয়নি) — `print-calibration.md`-এ ফ্যাক্টরির প্রিন্টারে ছাপিয়ে মাপার নির্ভুল পদ্ধতি আছে (M1 কাগজ ২১০×২৯৭ mm, M2 টেবিল-ফ্রেম প্রস্থ ১৮৭.১ mm, M3 ফ্রেম দৈর্ঘ্য Aug ১৬২.২ mm / May ২০৮.৮ mm, M4 title ৩৮.১ mm, M5 "780.0" ৭.৬ mm — সব ২০০ DPI স্ক্যান থেকে মাপা) |

**Wave 2a-তে ধরা পড়া regression (ঠিক করা হয়েছে):** ধাপ ৭-এর পর স্যুট ১৬/১৮-এ নেমে গিয়েছিল — নতুন font প্যানেল note-টিকে পাতার নিচে ঠেলে দিয়েছিল, pixel-diff ১০৯/১০৭ blob দেখেছিল। diff এখন `.page` element-এ সীমাবদ্ধ — আবার ১৮/১৮।

### ধাপ ৯ — Document DNA production-ready
| বিষয় | আগে (Round 1) | পরে (production) |
|---|---|---|
| Tracer | potrace 1.16 (GPL), IoU ০.৯৫০, ১০,৮৫২ B | **vtracer 1.0.0a4, IoU ০.৯৫৫** (digits ০.৯৬০, letters ০.৯৬৩), **৬,৭৪৮ B (−৩৮%)**, ০.৪ s — সবচেয়ে ছোট ও সবচেয়ে ভালো; img2bez ধীর (২৩–১১৯ s) ও খারাপ IoU |
| ওজন (weight) | একটাই ফন্ট | **Regular ৩৭ glyph + Bold ২১ glyph** — bold-এ **কোনো সংখ্যা নেই** (নথিতে bold সংখ্যা ছাপা হয় না); bold/regular stroke ১.৩১× (৩০০ ও ৬০০ DPI দুটোতেই); তৃতীয় semi-bold সেট নেই (subgroup ০.১৬৪/০.১৮২/০.১৮০ একটাই ব্যান্ড) |
| Cap height | ভুল ধারণা ৭৫৮u | **৭০০ unit দুটোতেই** — bold capitals regular-এর চেয়ে লম্বা নয় |
| রেজোলিউশন | ৩০০ DPI | **৬০০ DPI production** — ৬০০-DPI-reference IoU ০.৮১৮ → **০.৯৬৩**; staircase গড় segment ৫৪.৫u → **২৭.২u** (অর্ধেক); ফাইল +৬২% (১০,৯৬৮ → ১৭,৭৫৬ B), build ১.১ s → ২.৯ s |
| ৬০০ DPI বাগ | — | প্রথম ৬০০ DPI median cap ৩৬ trace px-এ বানানো হয়েছিল (৬০০ DPI নমুনা downscale করে) — ধরা পড়ে ঠিক করা হয়েছে (৩৬ @৩০০, ৭২ @৬০০) |
| Fallback chain | — | clone → **Liberation Serif (ওজন-মিলিয়ে)**; per-character audit (fontTools cmap; `document.fonts.check()` অবিশ্বস্ত — `.notdef`-এর কারণে না-থাকা অক্ষরেও true দেয়): BLISTER regular ৬/৭ clone, ১ fallback (B); "207/9" bold ০/৫ clone, ৫ fallback (সব সংখ্যা); CHECK bold ৩/৫ clone, ২ fallback (H, K); PRODUCT bold ৭/৭ clone; Serif বনাম Sans fallback IoU_fit ০.৫৬২ বনাম ০.৫৫১ — Serif রাখা হয়েছে |
| Matcher পুনঃ-চালনা | — | August DNA Bold ০.৬৫৫ / DNA Regular ০.৫২০; May DNA Bold ০.৫৮৪ / Sans Bold ০.৪৮২ / DNA Regular ০.৪৪৯; **Lot-এ DNA Regular দুই পাতাতেই জেতে** (Aug ০.৫৩৬, May ০.৫১৩); **WIDTH-এ Sans Bold জেতে** (Aug ০.৬৬২, DNA Regular ০.৫০৩; May ০.৬৯৫, DNA Regular ০.৩৮৫) — **প্রমাণিত sizing artifact, glyph-এর দোষ নয়**: `fs=box/0.7`-এ (বদলে `/0.85`) DNA Regular WIDTH-এও দুই পাতাতেই জেতে (Aug ০.৬৯২, May ০.৬৮২) |
| ডেমো প্রস্থ | — | Lot +৮.৭%/+৯.৩%, WIDTH +৩.৭%/+০.০%, REPORT −১.০% |
| v6 পাতায় integration | — | **DNA-ই ডিফল্ট rendering ফন্ট** (ওজন-মিলিয়ে); shortlist-এ DNA ১ম |
| ধরা পড়া regression (২টি, দুটোই ঠিক) | — | (১) font-loading race: fontfix-verify ৩১/৩৫ → ২৯/৩৫ (DNA webfont লোডের আগে fitWidth মাপা হয়েছিল) → `document.fonts.ready`-এর পর fitWidth আবার চালিয়ে ঠিক; (২) unhinted advance snapping: ২৯/৩৫ → ৩০/৩৫ (Chromium/FreeType unhinted advance-কে পূর্ণ পিক্সেলে snap করে, সর্বোচ্চ +১.৮ px) → fitWidth-কে বাক্সের ৯৭%-এ লক্ষ্য করে ঠিক; আসল ঠিক (ttfautohint) এই মেশিনে ইনস্টল নেই |

### ধাপ ১০ — Consolidation (এই রিপোর্ট — নিজে চালানো)
নিচের §২-এর পুরো টেবিল। কোনো ফেইল বা রিগ্রেশন পাওয়া যায়নি, তাই কোনো ঠিক-কাজের দরকার পড়েনি। একটি প্রমাণ প্রথম রানে **ভুল পদ্ধতিতে** চলেছিল (fallback-proof v1 — সব span একই জায়গায় বসানো হয়েছিল) — সেটি বাতিল করে সঠিক পদ্ধতিতে আবার চালানো হয়েছে (§২.৫ দেখুন)।

---

## ২. চূড়ান্ত যাচাই টেবিল (ধাপ ১০ — নিজে চালানো, ২০২৬-১১-০৬)

### ২.১ স্যুট

| যাচাই | ফল | মন্তব্য |
|---|---|---|
| `verify_round2.py` (v6 পাতা পুনর্নির্মাণ করে) | **১৮/১৮ PASS** | August ২,৭২৫,৪৯৬ B; May ১,০৫৫,৪৫২ B পুনর্নির্মিত |
| `fontfix-verify.py` | **৩১/৩৫ PASS** | ৪টি ফেইল ঠিক জানা সীমা — May title + PARAMETERS bold (stroke-পদ্ধতির সীমা, §৪.২) |
| `repro.py` | **PASS** | Lot "207/9" `.done` + clean ব্যাকগ্রাউন্ড; WIDTH "781.5" `.on` + clean ব্যাকগ্রাউন্ড |
| `manual_proof.py` | **১০/১০ PASS** | manual span "Bishow" + `.done`, manual clean ব্যাকগ্রাউন্ড, full-page bg geometry (৮২৫×১১৫৭), signature ঢাকা (residue ০), খালি manual বাক্স deactivate-এ সরিয়ে দেওয়া হয় |
| Pixel-diff (page-region) | **প্রতি পাতায় ঠিক ২টি blob** | August (১৭৭,৩১০,৩৩,১২) ও (৬৯৪,৪২৫,৩৪,১৫); May (১৭৩,৩০৪,৩৪,১৩) ও (৬৯১,৪২৮,৩৪,১৫) — ঠিক এডিট করা ২টি জায়গাতেই |

### ২.২ Identity probe — row label-সহ (অবস্থান একা যাচাই নয়)
| পাতা | এডিট | Span-এর টেক্সট | বাক্স | Row-এর পরিচয় |
|---|---|---|---|---|
| August | Lot | **"207/9"** (`.done`) | [৩৫৫,৬১৯,৪২১,৬৪৪] | Lot No. সারি (ব্যান্ডে ৮টি শব্দ) |
| August | WIDTH | **"781.5"** (`.on`) | [১৩৯১,৮৫৪,১৪৫১,৮৭৩] | Row-02 পুরো লাইন: 02. / WIDTH / mm / 780.0 / ± / 0.5mm / 781.5 (ব্যান্ডে ৭টি শব্দ) |
| August | Row-01 মান | **খালি, অপরিবর্তিত** | [১৩৯৬,৮১৩,১৪৪৭,৮৩২] | "Hard" অক্ষত ✓ |
| May | Lot | **"305/7"** (`.done`) | [৩৪৭,৬০৮,৪১৩,৬৩৩] | Lot No. সারি (ব্যান্ডে ৮টি শব্দ) |
| May | WIDTH | **"671.5"** (`.on`) | [১৩৮৪,৮৬০,১৪৪৫,৮৭৯] | Row-02 পুরো লাইন (ব্যান্ডে ৭টি শব্দ) |
| May | Row-01 মান | **খালি, অপরিবর্তিত** | [১৩৮৯,৮০৭,১৪৪১,৮২৭] | অক্ষত ✓ |

### ২.৩ Segmentation নমুনা (হাতে গোনা)
| পাতা | Rows ০১–০৫ | মোট শব্দ |
|---|---|---|
| August | **৩৭/৩৭** | ২৯৩ |
| May | **৩৩/৩৭** | ২৭৯ |

May title এখন ৩টি বাক্স, note লাইন ১৬টি বাক্স (ধাপ ১-এর বাগ ঠিক); August title-ও ৩টি পরিষ্কার বাক্স। পুরো পাতার ২৯৩/২৭৯টি বাক্স হাতে গোনা হয়নি — শুধু নমুনা।

### ২.৪ Doubling / D1 regression
| যাচাই | ফল |
|---|---|
| Doubling (২য় এডিটের পর) | Lot দুই পাতাতেই `.done` + নির্ভুল টেক্সট ধরে রাখে — **কোনো doubling নেই** |
| D1 (সব মুছে click-away) | span `.done` হারায়, মূল স্ক্যান পরিষ্কারভাবে ফিরে আসে — দুই পাতাতেই PASS |

### ২.৫ ধাপ-৯ integration — স্বাধীন যাচাই
| দাবি | যাচাই | ফল |
|---|---|---|
| DNA ফন্ট v6 পাতায় ডিফল্ট | built HTML-এর embedded ফন্টের SHA-256 | **byte-identical** — PGCloneDNA-Regular `fe1b608c094909f6` (৩৮ glyph), PGCloneDNA-Bold `5df18873de36f72f` (২২ glyph); **দুই পাতাতেই একই hash**; `dna-prod/dna-clone-regular-600.ttf` ও `dna-clone-bold-600.ttf`-এর সঙ্গে মেলে |
| পুরনো Round-1 potrace ফন্ট | — | **embedded নয়** — `improve/dna-clone.ttf` (SHA-256 `a36d74bfc26a0b8c`, ৩৬ glyph) v6 পাতায় নেই |
| Span-এর ডিফল্ট font-family | build_page.py v6 | ওজন-মিলিয়ে DNA + 'Liberation Serif', serif fallback |
| Fallback chain — clone-এ থাকা অক্ষর | pixel তুলনা (১০০ px, ২×): 'L' | **DNA-stack 'L' == clone-only 'L' ≠ Liberation 'L'** (dark px ৫,৪৮১ বনাম ৬,৫১৫) — clone-ই ব্যবহৃত হয় ✓ |
| Fallback chain — clone-এ না-থাকা অক্ষর | pixel তুলনা: 'B' | **DNA-stack 'B' == Liberation Serif 'B'** (২৪,৬১৩ dark px, pixel-identical) — না-থাকা অক্ষর Liberation Serif-এই render হয় ✓ |
| Fallback প্রমাণের সীমা | — | এই মেশিনে system fallback-ও Liberation Serif-এ গিয়ে পৌঁছায়, তাই পরীক্ষাটি **render করা ফলাফলটি** প্রমাণ করে (stack-এর নাম ধরে fallback বনাম system fallback আলাদা করা যায়নি) — stack-এ Liberation Serif স্পষ্ট নামে আছে, ফলাফল প্রতিশ্রুতি মতোই |
| Fallback v2 প্রচেষ্টা | mixed-span গঠন | **পদ্ধতিগতভাবে বাতিল** — এক-span বনাম multi-span শব্দের canvas উচ্চতা আলাদা হয় (২০৪ বনাম ২১৬ px), তাই pixel তুলনা অর্থহীন; এটি product-এর দোষ নয়, প্রমাণের পদ্ধতির দোষ |

### ২.৬ চোখে দেখা (eye-check — নিজে দেখা স্ক্রিনশট)
| জায়গা | ফাইল | যা দেখা গেল |
|---|---|---|
| August Lot row (২×) | `cons-aug-lot-2x.png` | "Lot No. : 207/9" — পরিষ্কার, ghost/doubling নেই, DNA ফন্ট আশপাশের ছাপের সঙ্গে মিশে যায় ✓ |
| May Lot row (২×) | `cons-may-lot-2x.png` | "Lot No. : 305/7" — পরিষ্কার, তীক্ষ্ণ B&W ✓ |
| August WIDTH row 02 (২×) | `cons-aug-width-2x.png` | "Hard" অক্ষত; "781.5" নীল-ঘেরা active span-এ পরিষ্কার; নিচে 0.0251, 68.02 অক্ষত ✓ |
| May WIDTH row 02 (২×) | `cons-may-width-2x.png` | "Hard" অক্ষত; "671.5" পরিষ্কার; নিচে 0.0204 অক্ষত ✓ |
| August title (২×) | `cons-aug-title-2x.png` | "ANALYTICAL TEST REPORT" — ধূসর বার + আন্ডারলাইন অক্ষত; "PRODUCT: BLISTER FOIL" অক্ষত ✓ |
| DNA title REPORT (২×) | `dna-prod-clip-aug-title-report-2x.png` | DNA Bold "REPORT" মূলের সবচেয়ে কাছে (Liberation Serif Bold-এর serif চেহারা স্পষ্ট আলাদা) ✓ |
| Fallback (২×) | `dna-prod-clip-fallback-2x.png` | "BLISTER" পুরো render হয় (tofu নেই) — কিন্তু **serif B sans clone অক্ষরের মাঝে চোখে ধরা পড়ে** (ওজন মেলে, style মেলে না — §৪.৫) |

---

## ৩. ব্যর্থতা / খোলা বিষয় (ধাপ ১০)

**কোনো ফেইল বা রিগ্রেশন পাওয়া যায়নি।** সব স্যুট আগের রিপোর্টের সংখ্যার সঙ্গে হুবহু মিলেছে (১৮/১৮, ৩১/৩৫, repro PASS, manual ১০/১০)। তাই কোনো ঠিক-কাজ করা হয়নি, কোনো ধাপ পুনর্নির্মাণ করা হয়নি। নিচের §৪-এর সীমাগুলোই খোলা বিষয় — এগুলো ডিজাইন-সিদ্ধান্ত বা পরের রাউন্ডের কাজ, গোপন ত্রুটি নয়।

---

## ৪. সৎ সীমা (এখনও যা নিখুঁত নয়)

1. **WIDTH সংখ্যার sizing:** `/0.85` নিয়ম সংখ্যা-শুধু শব্দকে ~২১% ছোট করে; `fs=box/0.7`-এ DNA Regular WIDTH-এও জেতে (Aug ০.৬৯২, May ০.৬৮২) — কিন্তু global নিয়ম বদলানো হয়নি (সব যাচাই বদলে যেত)। **পরের কাজ: per-word cap-height sizing।**
2. **May title + PARAMETERS bold:** fontfix-verify-এর ৪টি ফেইল — May title-এর ৩টি শব্দ + PARAMETERS হেডার; খুব bold stroke মাপার stroke-পদ্ধতির প্রমাণিত সীমা।
3. **কাগজে print calibration:** হয়নি — এই VM-এ প্রিন্টার নেই; ফ্যাক্টরির প্রিন্টারে ছাপিয়ে মাপতে হবে (পদ্ধতি `print-calibration.md`-এ)।
4. **হাতের লেখা / stamp:** stamp detector দুই পাতাতেই কিছু পায়নি — B&W পাতায় রঙ দিয়ে stamp চেনা অসম্ভব; manual-box বাক্সের বাইরে residue রেখে যায়; খালি manual বাক্স deactivate-এ সরিয়ে দেওয়া হয় (ইচ্ছাকৃত নকশা)।
5. **DBNet:** spike GO (শর্তসহ), কিন্তু integration-এ regressed → classical-ই primary; আসল i5-8265U-তে সময় মাপা হয়নি।
6. **Hinting নেই:** ttfautohint এই মেশিনে ইনস্টল নেই — ০.৯৭ fitWidth margin শুধু workaround (unhinted advance snapping সর্বোচ্চ +১.৮ px)।
7. **Fallback style clash:** serif B sans clone অক্ষরের মাঝে ২×-এ চোখে ধরা পড়ে (ওজন মেলে, style মেলে না)।
8. **Title bar clean layer:** live v4 clean টাইটেলকে ~২৪৫ ধূসর সাদা করে দেয়; bar-aware fill দরকার (bar median ~১৮৪)।
9. **Bold ফন্টে সংখ্যা নেই** (নকশাগত — নথিতে bold সংখ্যা ছাপা হয় না); glyph সংখ্যা Regular ৩৭ / Bold ২১ — বাকি সব fallback-নির্ভর।
10. **৬০০ DPI-র খরচ:** ফাইল +৬২%, build ১.১ s → ২.৯ s।
11. **এডিট এখনও শুধু live পাতায়:** স্ক্যান-এডিট PDF-এ ফিরিয়ে লেখা (write-back) বা DB রেকর্ড এখনও নেই — এগুলো production পথের কাজ।
12. **Segmentation পুরো পাতা হাতে গোনা হয়নি:** শুধু rows ০১–০৫ নমুনা (Aug ৩৭/৩৭, May ৩৩/৩৭)।
13. **LaMa ব্যবহার হয়নি; MI-GAN NO-GO; Telea-ই ডিফল্ট inpainter।**

---

## ৫. লাইসেন্স — আপডেটেড চিত্র (কারিগরি গবেষণা, আইনি পরামর্শ নয়)

| বিষয় | অবস্থা |
|---|---|
| **potrace (GPL-2.0-or-later)** | **production ফন্টে আর নেই।** v6 পাতায় embedded ফন্ট vtracer-দিয়ে বানানো (byte-identical যাচাই, §২.৫)। potrace build-time CLI fallback হিসেবেই থাকে; এই মেশিনে potrace ইনস্টলই নেই (`which potrace` → কিছুই নেই)। পুরনো Round-1 potrace ফন্ট (`dna-clone.ttf`) শুধু গবেষণা-ফাইলে আছে, পাতায় নয় |
| **vtracer** | **MIT OR Apache-2.0 (dual)** — GitHub metadata + Cargo.toml থেকে VERIFIED (LICENCE-GROUNDWORK.md)। একটিমাত্র সাবধানতা: LICENSE ফাইলের copyright-holder লাইনটি আলাদা করে পড়া হয়নি (**UNVERIFIED**) |
| **US পেটেন্ট US20150332491A1** | অস্তিত্ব VERIFIED; granted/in-force অবস্থা, claim-এর পরিধি, বাংলাদেশে প্রযোজ্যতা **যাচাই হয়নি — বিক্রির আগে আইনি যাচাই বাধ্যতামূলক** |
| **LaMa / Places2** | ব্যবহার হয়নি — pipeline-এ LaMa-র কোনো code, weight বা reference নেই |
| **MI-GAN** | code + weights MIT VERIFIED, কিন্তু **নেওয়া হয়নি** (NO-GO) — pipeline-এ নেই |
| **Clone glyphs** | শুধু local rendering aid — standalone ফন্ট হিসেবে বিতরণ করা যাবে না |

---

## ৬. এরপর কী (Round 3-এর প্রার্থী)

1. **Per-word cap-height sizing** — WIDTH সংখ্যার sizing ঠিক করবে (DNA তখন WIDTH-এও জেতে)।
2. **ttfautohint hinting** — ০.৯৭ fitWidth margin সরিয়ে দেবে।
3. **Bar-aware clean fill** — title bar-এর ধূসর (~১৮৪) ঠিক রাখবে।
4. **DBNet title fragmentation ঠিক + primary swap পুনঃমাপন + i5-8265U-তে সময়** — C4 শর্ত পূরণ হলে তবেই swap।
5. **ফ্যাক্টরির প্রিন্টারে print calibration** (M1–M5, `print-calibration.md`)।
6. **আরও নথি থেকে আরও glyph** — DNA ফন্টের glyph সংখ্যা বাড়ানো।
7. **PDF write-back + DB রেকর্ড** — এডিট করা স্ক্যানকে production পথে নেওয়া।
8. **US পেটেন্টের আইনি যাচাই** — বিক্রির আগে বাধ্যতামূলক।

---

## ৭. ফাইল তালিকা (Round 2)

| ফাইল | বিষয় |
|---|---|
| `improve/round2/step1-2-report.md` | ধাপ ১–২ (lossless background + mask fix) |
| `improve/round2/dbnet/` | ধাপ ৩ DBNet spike (ONNX + রিপোর্ট) |
| `improve/round2/migan/` | ধাপ ৪ MI-GAN spike (ONNX + রিপোর্ট) |
| `improve/round2/step5-8-report.md` | ধাপ ৫–৮ (deskew/confidence, Grain v2, matcher/shortlist, manual-box/stamp/print) |
| `improve/round2/print-calibration.md` | ধাপ ৮c — প্রিন্ট পদ্ধতি |
| `improve/round2/dna-prod/` | ধাপ ৯ DNA production (রিপোর্ট, ৬০০ DPI ফন্ট, tracer spike, matcher rerun) |
| `improve/round2/licences/LICENCE-GROUNDWORK.md` | লাইসেন্স গবেষণা (কারিগরি, আইনি পরামর্শ নয়) |
| `improve/round2/verify_round2.py` | ১৮/১৮ স্যুট |
| `improve/round2/cons-*-1x/2x.png` | ধাপ ১০-এর চোখে-দেখা ক্লিপ (Lot/WIDTH/title, দুই পাতা) |
| `improve/round2/fb-{dna,lib,clo}-{B,L}.png` | Fallback প্রমাণের স্ক্রিনশট |
| `live-scan-page.html` / `live-scan-page-may.html` | **v6 live পাতা** (DNA ডিফল্ট ফন্ট) |
| `improve/ROUND2-REPORT.md` | **এই রিপোর্ট** |

**নোট:** এই রিপোর্টটি Drive-এ আপলোড করা হয়নি, `REPORT.md` / `REPORT-MAY.md` বদলানো হয়নি — parent-এর নির্দেশ অনুযায়ী সেগুলো parent-এর হাতে।
