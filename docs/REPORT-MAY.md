# Live-Scan — মে ২০২৬ পাতার পরীক্ষা (May B&W Scan Test)

> **প্রযুক্তি: Live-Scan** — একই pipeline, দ্বিতীয় আসল পাতায় পরীক্ষা।
> আসল ফাইল: "PG MAY-2026 (20mic) COA.pdf" — পাতা ১, ৩০০ DPI সাদা-কালো (CCITT) স্ক্যান, শূন্য extractable text।
> মূল রিপোর্ট: `REPORT.md` (অগাস্টের রঙিন পাতা)। এই ফাইলে শুধু মে পাতায় যা পাওয়া গেল — ভালো আর খারাপ, দুটোই।

---

## ১. পাতাটি কী

- **উৎস:** `~/workspace/gravora-review/packfirm-analysis/supplier-coa/PG MAY-2026 (20mic) COA.pdf` — ৬ পাতা, প্রতিটি ৩০০ DPI সাদা-কালো স্ক্যান।
- **পাতা ১:** PG Foils Ltd.-এর ANALYTICAL TEST REPORT — PRODUCT: BLISTER FOIL, 20 Micron, Lot No. 304/5, Quantity 1063.36 Kgs, ১৮-সারির test table, Conclusion, Test Condition, Prepared By / Approved By — হাতে লেখা স্বাক্ষর ও তারিখসহ (19/05/26)।
- অগাস্টের পাতার মতোই PG টেমপ্লেট, কিন্তু **সাদা-কালো স্ক্যান** — এটাই পরীক্ষার আসল উদ্দেশ্য: B&W-তে Live-Scan চলে কি না।

## ২. যা চালানো হয়েছে — একই pipeline, একই প্যারামিটার

```
PDF পাতা → 200 DPI PNG (pages/may-p1-1.png — আগেই তোলা ছিল) → segment.py → inpaint.py → build_page_may.py
```

| ধাপ | ফল |
|---|---|
| Page extract | `pages/may-p1-1.png` — 1650×2314, RGB (আগের রানের ফাইল, আবার তোলা হয়নি) |
| Segmentation | `seg-may-p1.json` — **২৬৯টি শব্দ, ৩৯টি লাইন**, median component height 18 px (অগাস্ট: ৩০২টি শব্দ, ৪৪ লাইন, 17 px) |
| Inpainting | `pages/may-p1-clean.png` — ২৬৯টি box, ২৯৫,৮৮২ masked pixel (পাতার **৭.৭৫%**) |
| Live page | `live-scan-page-may.html` (১,৩২২,৮৬১ bytes) — মূল স্ক্যান background + ২৬৯টি span; demo: Lot 304/5 → 305/7, WIDTH 670.0 → 671.5 |
| Demo edit | Playwright probe + pixel-diff দিয়ে যাচাই (নিচে §৫) |

**কিছুই বদলানো হয়নি:** segment.py / inpaint.py-র threshold, LOGO/SIGROW মান, gap threshold — সব অগাস্টের মতোই। উদ্দেশ্য ছিল দেখা — একই সেটিং অন্য স্ক্যানে চলে কি না। উত্তর: **মূলত চলে, কিন্তু দুটি নির্দিষ্ট জায়গায় ভাঙে** (§৪)।

## ৩. মাপা নির্ভুলতা — Segmentation (হাতে যাচাই করা নমুনা, অগাস্টের মতোই পদ্ধতি)

টেস্ট-টেবিলের সারি ০১–০৫ — মূল স্ক্যান থেকে চোখে গুনে সত্যিকারের শব্দ, তারপর box-এর সঙ্গে মেলানো।

| সারি | সত্যিকারের শব্দ (চোখে গোনা) | Segmented box | মিল |
|---|---|---|---|
| 01 | 01. / DESCRIPTIONS / - / FOIL / TEMPER / Hard = **৬** | ৫ | FOIL+TEMPER এক box-এ জোড়া; "-" শুধু ৭×৩ px sliver (ফিকে ছাপা, নিচে দেখুন) |
| 02 | 02. / WIDTH / Mm / 670.0 / (± / 0.5mm) / 670.0 = **৭** | ৭ | ৭/৭ ✅ |
| 03 | 03. / ALU. / THICKNESS / mm / 0.0184 / – / 0.0216 / 0.0204 = **৮** | ৮ | ৮/৮ ✅ |
| 04 | 04. / ALU. / GRAMMAGE / gms/m² / 49.86 / – / 58.54 / 55.28 = **৮** | ৭ | "–"+"58.54" এক box-এ জোড়া |
| 05 | 05. / HSL / GRAMMAGE / gms/m² / 6.0 / – / 8.0 / 7.32 = **৮** | ৬ | HSL+GRAMMAGE জোড়া; "–"+"8.0" জোড়া |
| **মোট** | **৩৭** | **৩৩** | **৩৩/৩৭ box-গণনায় (অগাস্ট: ৩৭/৩৭)** |

**সৎ ব্যাখ্যা:** কোনো শব্দ পুরোপুরি হারায়নি — জোড়া লাগা box-গুলোতে দুটি শব্দের pixel-ই ঢাকা আছে, ক্লিক-এডিট চলে (দুটি শব্দ একসঙ্গে retype করতে হয়)। আসল দুর্বলতা দুটি:
- **ছোট gap-এ জোড়া লাগা:** B&W স্ক্যানে bold অক্ষরের মাঝের ফাঁক কম — gap threshold (0.35×median height) কখনো কখনো দুটি শব্দকে এক করে দেয়। অগাস্টের রঙিন স্ক্যানে এটা হয়নি।
- **ফিকে ছাপা:** সারি ০১-এর "-" ড্যাশ স্ক্যানেই প্রায় অদৃশ্য — ওই cell-এ mean gray ২৫২.৮, dark pixel মাত্র ০.৯% (তুলনায় DESCRIPTIONS cell-এ ২৪.১%)। Otsu সেখান থেকে মাত্র ৭×৩ px sliver পেয়েছে। এটা স্ক্যানের দোষ, segmentation-এর নয় — কিন্তু box-টা ক্লিক করার মতো ছোট।

**নমুনার বাইরে, হেডার:** টেবিল হেডার (S.No. / TEST / PARAMETERS / UNIT / STANDARD / LIMIT / OBSERVATIONS) — **৭/৭ ✅**। Quantity সারি: ৪টি শব্দ ঠিক, সঙ্গে বাঁ মার্জিনে একটি ৩×৩ px scanner-noise speck-এর ভুল box (লাইন ১৩)।

## ৪. দুটি আসল বাগ — পুরো পাতায় যা ধরা পড়ল

### বাগ ১ — শিরোনাম "ANALYTICAL TEST REPORT" segmentation-এ আসেইনি

- শিরোনামটি বড় bold + underline + পেছনে ধূসর highlight (dithered)। Otsu-তে অক্ষরগুলো highlight-এর সঙ্গে জুড়ে **একটাই ৩০০×৩৫ px component** হয়ে যায় (area ৬,৫৪৮)।
- ওই component-এর কেন্দ্র (cy ৪০৮) আর পাশের ছোট sliver-গুলোর কেন্দ্র (cy ~৩৯১) থেকে ১৫–১৭ px দূরে — line-grouping tolerance (max ৬, 0.6×median = ১০.৮ px) পেরিয়ে যায়। তাই component-টি **একা একটি লাইন হয়, আর `len(items) >= 2` ফিল্টারে বাদ পড়ে যায়**।
- ফল: `seg-may-p1.json`-এ শিরোনামের **৩টি শব্দ নেই**; inpainting-ও সেটা মোছেনি — clean পাতায় শিরোনাম প্রায় পুরোটাই **ধূসর ভূত (ghost) হয়ে রয়ে গেছে** (may-title-clean.png-এ চোখে দেখা)। "PRODUCT: BLISTER FOIL" ঠিকমতো মুছেছে — শুধু শিরোনামটাই বাকি।
- অগাস্টের পাতায় এটা হয়নি — সেখানে শিরোনামের অক্ষর এক component-এ জোড়া লাগেনি।

### বাগ ২ — নিচের নোটের লাইন SIGROW-তে কাটা পড়েছে

- পাতার নিচের লাইন — "If any deviation found in the concern material Please provide the related stickers / details for investigation." (১৭টি শব্দ) — y ~১৯৯৩–২০১৫-তে বসে।
- `segment.py` / `inpaint.py`-তে signature-row exclusion **hardcoded SIGROW y=2000**। নোটের অক্ষরের কেন্দ্র ২০০০ পেরিয়ে যায় বলে সেগুলো "হাতের লেখা" ভেবে বাদ দেওয়া হয়েছে — শুধু অক্ষরের মাথার ৩–৪ px sliver (১০টি, লাইন ৩৮) বেঁচেছে।
- ফল: clean পাতায় নোটের লাইনটি **পুরোপুরি অক্ষত** রয়ে গেছে — এডিটের সময় ওই লাইনের শব্দে ক্লিক করলে inpainted background পাওয়া যাবে না।
- স্বাক্ষরের সারি আসলে y ~২০৫০-এর নিচে; নোট y ~১৯৯৩-এ। Hardcoded ২০০০ দুটোকে আলাদা করতে পারেনি।

**এই দুটির মানে:** মে পাতায় মোট ~২৯০টি সত্যিকারের শব্দের মধ্যে **~২০টি শব্দের box নেই** (শিরোনাম ৩ + নোট ১৭) — প্রায় **৯৩% word coverage**। টেবিলের মূল অংশ (যেখানে আসল এডিট হয়) ৩৩/৩৭ — কাজ করে। কিন্তু "যেকোনো স্ক্যানে" দাবি করতে হলে এই দুটি ঠিক করতেই হবে।

## ৫. ডেমো এডিট — যাচাই (প্রমাণসহ)

| এডিট | লক্ষ্য শব্দ (segmentation box) | Probe-এ পাওয়া অবস্থান | ফল |
|---|---|---|---|
| Lot No. **304/5 → 305/7** | box (347, 608, 66×25) | left 211, top 454 (page offset-সহ image y 620-র সঙ্গে মেলে) ✅ | ✅ সঠিক শব্দে |
| WIDTH Observation **670.0 → 671.5** | box (1384, 860, 61×19) | left 730, top 580 (image y 869-র সঙ্গে মেলে) ✅ | ✅ সঠিক শব্দে |

Pixel-diff (plain vs edited screenshot, viewport): **৫২৪টি pixel বদলেছে, ঠিক ২টি জায়গায়** — Lot-এর জায়গায় ২টি blob (211,455 + 226,459 — "304/5"→"305/7"-এ শুধু বদলে যাওয়া glyph) আর WIDTH-এর জায়গায় ১টি blob (728,578)। পাতার আর কোথাও কিছু বদলায়নি। স্ক্রিনশট চোখে দেখা হয়েছে: Lot-এ 305/7, WIDTH-এ 671.5 — বাকি পাতা অক্ষত, স্বাক্ষর অক্ষত।

## ৬. Inpainting-এর মান — চোখে দেখা (may-p1-clean.png)

- টেবিলের লাইন, লোগো, দুটি হাতের স্বাক্ষর **অক্ষত**।
- **বাকি থাকা artifact (সৎ তালিকা):**
  - শিরোনাম "ANALYTICAL TEST REPORT"-এর ধূসর ভূত (বাগ ১)।
  - নিচের "If any deviation…" লাইন পুরোপুরি রয়ে গেছে (বাগ ২)।
  - UNIT কলামে `²` superscript-এর ভূত — ৪টি সারিতে (০৪, ০৫, ০৬, ১১) — অগাস্টের মতোই, একই কারণ (box-এর ভেতরের ছোট superscript পুরোপুরি mask হয় না)।
  - ওপর-ডানদিকে একটি ছোট speck ডট (মূল স্ক্যানের noise)।
- Bold অনুমান আগের মতোই over-bold: **২৬৫/২৬৯টি শব্দ bold** ধরা হয়েছে — B&W স্ক্যানে ink density বেশি বলে আরও খারাপ (REPORT.md §৯ item 4-এর threshold-ঠিক করা এখনো বাকি)।

## ৭. সিদ্ধান্ত — মে পাতা কী প্রমাণ করল, কী করল না

| দাবি | অবস্থা |
|---|---|
| B&W স্ক্যানেও Live-Scan-এর মূল টেবিল এডিট চলে | ✅ প্রমাণিত — Lot + WIDTH ডেমো, pixel-diff-সহ |
| অন-এডিটেড পিক্সেল ১০০% অপরিবর্তিত (by construction) | ✅ আগের মতোই (JPEG q88 re-encode caveat একই) |
| Segmentation নমুনা (সারি ০১–০৫) | 📏 **৩৩/৩৭ box** (অগাস্ট ৩৭/৩৭); জোড়া লাগা ৪টি, ফিকে "-" ১টি |
| পুরো পাতার word coverage | ⚠️ **~৯৩%** — শিরোনাম ৩ + নোট ১৭টি শব্দের box নেই (বাগ ১+২) |
| Inpainting | 👁️ টেবিল/লোগো/স্বাক্ষর অক্ষত; শিরোনাম ভূত + নোট অক্ষত (বাগ ১+২) |
| Font মিল | ⚠️ Approximation; bold over-estimate আরও বেশি (২৬৫/২৬৯) |

**পরের দুটি নির্দিষ্ট ঠিক (REPORT.md §৯-এর item 5 সম্পন্ন, নতুন কাজ):**
1. **Singleton-line ফিল্টার বদলানো:** একা বড় component (যেমন শিরোনাম) ফেলে না দিয়ে আলাদাভাবে word box করা — বা component-এর আকার দেখে সিদ্ধান্ত নেওয়া।
2. **SIGROW hardcoded y=2000 তুলে দেওয়া:** স্বাক্ষরের সারি প্রতি পাতায় মেপে বের করা (যেমন নিচের ১৫%-এ হাতের লেখা/স্বাক্ষর খোঁজা), যাতে নোটের মতো ছাপা লাইন কাটা না পড়ে।

## ৮. ফাইল তালিকা (`scan-paper/` — নতুন)

- `seg-may-p1.json` — ২৬৯টি word box (মে পাতা ১)
- `pages/may-p1-clean.png` — inpainted background (মে পাতা ১)
- `pages/may-p1-segview.png` — সব box লাল দাগে আঁকা পুরো পাতা
- `pages/may-clip-rows01-05.png` — সারি ০১–০৫-এর ১.৫× crop, box-সহ (হাতে গোনার প্রমাণ)
- `pages/may-zoom-r02-unit.png`, `may-zoom-r01-std.png`, `may-zoom-r01-test.png` — zoom crop
- `pages/may-title-orig.png`, `pages/may-title-clean.png` — শিরোনাম: আসল বনাম clean
- `build_page_may.py` — মে পাতার live page বানানোর স্ক্রিপ্ট (build_page.py-র parameterised কপি)
- `live-scan-page-may.html` — মে পাতার live page (খুলে ক্লিক করে এডিট করা যায়; `?demo=1` ডেমো এডিট)
- `shots-may-page-plain.png`, `shots-may-page-edited.png` — ডেমো স্ক্রিনশট
- `REPORT-MAY.md` — এই ফাইল

---

## ৯. দুটি বাগ ঠিক করা হয়েছে (২০২৬-১১-০৬, segmentation ট্র্যাক)

**বাগ ১ — শিরোনাম:** `segment.py` v2-এ singleton-line rescue — dark-ink threshold (`0.65 × Otsu`), solid-rule সারি ফেলে দেওয়া, letter-উচ্চতার টুকরো, running-max edge দিয়ে word-গ্রুপ (`max(3, 0.15 × med_h)`)। শিরোনাম এখন **৩টি box**: `[672, 395, 814, 418]` / `[817, 397, 875, 418]` / `[880, 397, 971, 418]` (ANALYTICAL / TEST / REPORT)। Highlight-কিনারার ৩টি ভুয়া sliver box বাদ গেছে। Browser যাচাই: TEST-এ `CHECK` টাইপ করে ক্লিক সরিয়ে দেখা — পরিষ্কার `CHECK`, কোনো doubling নেই, ভূতের লেখা আর পড়া যায় না। **বাকি artifact:** Telea highlight-এর ধূসর রঙ ছড়িয়ে হালকা ফিতা রেখে গেছে (band mean grey ১১১.৫ → ১৬০.৫) — অক্ষরের আকৃতি নেই, কিন্তু zoom করলে চোখে পড়ে; inpaint ট্র্যাকের জন্য নোট করা আছে।

**বাগ ২ — SIGROW:** hardcoded `y=2000` তুলে per-page detection — নিচের ৩০%-এ `h > 2.2 × median` আঁচড় ≥ ২টি থাকলে `sig_y` = সবচেয়ে ওপরের আঁচড়ের y। মে: **`sig_y=2106`** — নোটের লাইন (১৭টি শব্দ → ১৬টি box, `/` পাশের box-এ) আর "Prepared By:" / "Approved By:" লেবেল (৪টি box) এখন এডিট করা যায়; স্বাক্ষর অক্ষত (inpaint-এ MAD ০.০)। একই detection `inpaint.py`-তেও বসানো হয়েছে। Browser যাচাই: নোটের "deviation" → "variation" ঠিক জায়গায়, বাকি লাইন অক্ষত।

**আগে/পরে সংখ্যা:**

| | আগে | পরে |
|---|---|---|
| মে শব্দ (box) | ২৬৯ | **২৭৯** |
| শিরোনাম box | ০ | **৩** |
| নোটের লাইন box | ১০টি sliver | **১৬টি box (১৭টি শব্দ)** |
| Prepared/Approved By লেবেল box | ০ | **৪** |
| নমুনা সারি ০১–০৫ | ৩৩/৩৭ | **৩৩/৩৭ (অপরিবর্তিত — একই ৪টি জোড়া লাগা)** |
| পুরো পাতার coverage | ~৯৩% | **~২৮০টি সত্যিকারের শব্দের সবগুলো কোনো box-এ ঢাকা** |
| অগাস্ট শব্দ (box) | ৩০২ | **২৯৩** (৯টি স্বাক্ষরের আঁচড়-“শব্দ” গেছে; আসল শব্দ যায়নি) |
| অগাস্ট নমুনা সারি ০১–০৫ | ৩৭/৩৭ | **৩৭/৩৭ (অপরিবর্তিত)** |
| অগাস্ট ডেমো + doubling repro | পাস | **আবার পাস (probe.py + repro.py)** |

ফাইল: `segment.py` v2, `inpaint.py` v2, `seg-may-p1.json` (২৭৯), `seg-aug-p1.json` (২৯৩), `pages/may-p1-clean.png`, `pages/aug-p1-clean.png`, `live-scan-page-may.html`, `live-scan-page.html` (দুটোই আবার বানানো; May পাতায় `?demo=1`/`?boxes=1` এখন build থেকেই চলে)। যাচাইয়ের স্ক্রিনশট: `improve/seg-may-*.png`। গবেষণা: `improve/research-segmentation.md` (DBNet det-only ONNX + projection-profile word-split, হাতের লেখা, স্ট্যাম্প, skew/low-res, confidence)।

---

## ডাবলিং বাগের ঠিক (২০২৬-১১-০৬)

অগাস্ট পাতায় ব্যবহারকারী নিজে যে doubling বাগ ধরেছিলেন (এডিট করা শব্দে ক্লিক সরে গেলেই আসল লেখা টাইপ করা লেখার নিচে ভেসে উঠত), সেই একই দোষ মে পাতাতেও ছিল। `build_page_may.py`-তে একই ঠিক (`.done` class) লাগিয়ে পাতাটি আবার বানানো হয়েছে। বিস্তারিত `REPORT.md` §১১-এ।
