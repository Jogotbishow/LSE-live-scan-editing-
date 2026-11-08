# LSE সম্পূর্ণ — প্রতিবেদন

**তারিখ:** ২০২৬-১১-০৮
**কাজ:** LSE (Live-Scan Editing) সম্পূর্ণ করা + public GitHub repo `live-scan-editing` (MIT)
**অবস্থা:** staging তৈরি ও যাচাই শেষ; repo প্রকাশ ব্যবহারকারীর অনুমোদনের অপেক্ষায় (নিচে দেখুন)

## যা সম্পূর্ণ হয়েছে

### ১. একাধিক পাতা (Multi-page)
- নতুন Document API (`lse/document.py`) — `page: 1` hardcode সরানো হয়েছে।
- PG AUGUST-2026 (৮ পাতা) ও PG MAY-2026 (৬ পাতা) — native 300 DPI-তে যাচাই, সম্পাদনা + write-back + DB রেকর্ড সহ।
- `tests/test_multipage.py` — full suite-এর অংশ হিসেবে পাস।

### ২. লেবেল Domino (Save → label)
- `Document.save_with_label()` — স্ক্যান সেভ করলেই লেবেল আপনা-আপনি তৈরি হয় (xlsx-র মতো)।
- `tests/test_save_label.py` — ৫/৫ (synthetic ACME + আসল PG Aug পাতা; কখনো ডেমো মান নয়)।
- লেবেলের Batch/Mfg Date আসল COA থেকে আসে — যাচাই করা হয়েছে।

### ৩. সিদ্ধান্ত (reversible — ব্যবহারকারী যেকোনো সময় বদলাতে পারেন)
`lse/DECISIONS.md` §১–§৭-এ লেখা আছে:
- **§১ -2 band নিয়ম:** ACCEPT — band-আকৃতির core (cw>120) mask থেকে বাদ।
- **§২ Caps:** প্রস্তাব B — caps না বসলে lowercase পরামর্শ (কখনো চাপিয়ে ছোট করা নয়)।
- **§৩ Gate:** শুধু quality check, ship-gate নয়; T1 0.50 অপরিবর্তিত।
- **§৪ Bold:** Lot-anchor + heading flip নকশা; নতুন template-এ automatic bold detection নয়।
- **Q-03–Q-09, ★2–★8:** এখানে সিদ্ধান্ত হয়নি — এগুলো ব্যবহারকারীরই আছে।

### ৪. Repo প্যাকেজিং
- MIT LICENSE, README (install/run, নিজের scan-এ test, Windows setup), API.md, docs ROUND2–ROUND18।
- `.gitignore` — আসল PG/Raviraj/Amcor COA, `*.db`, demo binary বাদ।
- Demo শুধু synthetic ACME (Batch ACME-2026-0001, Lot ACME-LOT-77 — সব ভুয়া); আসল COA/DB কখনো public-এ যাবে না।

## যাচাই (আমার নিজের চালনা, ২০২৬-১১-০৮)

- **Full suite:** `tests/run_all.py` — **৩৮টি test, ০ failure, ০ error, ০ skipped** (exit 0)।
- **Demo পথ:** `demo/make_synthetic.py` → `python -m lse.segment demo/synthetic-supplier-coa-300.png /tmp/seg.json` → **৮২ শব্দ** (ground truth ৭৮; batch/lot hyphen-এ ভেঙে +৪)। ground-truth JSON দুই রানে byte-identical (md5 `7a5a1dcdbd8f3e9e668677c8243f65b9`)।
- **প্রকাশের আগের ২টি ত্রুটি ঠিক করা হয়েছে:**
  1. README লাইন ৮৮ ও ১০৮ — `python lse/segment.py ...` ImportError দিত; এখন `python -m lse.segment ...`।
  2. Test portability — `tests/helpers.py`-তে আসল PG PDF/DNA font-এর absolute local path hardcode ছিল; clean clone-এ test-গুলো error দিত। এখন `requires_real_fixtures` (skipUnless) — ১২টি real-fixture class clean clone-এ skip করে (exit 0), portable test-গুলো (gate constants, row-label mapping) চলে।
  3. README "How to test" সংশোধন — পুরোনো দাবি ("tests run on synthetic sample only") ভুল ছিল; full suite আসল PG/DNA fixture চায়, যা repo-তে নেই; clean clone-এ demo পথই যাচাইয়ের উপায়।

## সৎ সীমা (অপরিবর্তিত)

- Gate: নতুন ২৫টি Raviraj পাতায় **৯ ALLOW / ১৬ REFUSE** — segmentation এখনো সব পাতায় নিখুঁত নয়।
- Universality: অন্য ছাপা নথিতে দুর্বল (FUNSD ৪৭.৪%, SROIE ১৮.৮%, Tottel ৭০.৮%); হাতে-লেখা (cursive) প্রায় চলে না।
- প্রিন্ট ক্যালিব্রেশন ও পেটেন্ট-যাচাই ব্যবহারকারীর হাতে (তাঁর নির্দেশ অনুযায়ী)।
- GRAVORA অ্যাপে LSE integration আলাদা কাজ — এখানে শুধু standalone engine + repo।

## Repo প্রকাশ — অবস্থা

- GitHub অ্যাকাউন্ট নিশ্চিত: **Jogotbishow** (https://github.com/Jogotbishow)।
- Staging-এ git init করা, **৬৭টি ফাইল** (কোনো binary নয় — demo PDF/PNG ও label আউটপুট gitignore করা)।
- **Repo এখনো বানানো হয়নি:** public repo বানাতে GitHub write-এর অনুমোদন লাগে — প্রথম কার্ড ৩০ মিনিটে approve না হওয়ায় মেয়াদ শেষ। ব্যবহারকারী অনুমোদন দিলেই `live-scan-editing` (public, MIT) বানিয়ে push করা হবে, তারপর clean-clone যাচাই ও লিংক দেওয়া হবে।
- Repo URL: https://github.com/Jogotbishow/LSE-live-scan-editing- (ব্যবহারকারী নিজে বানিয়েছেন, ২০২৬-১১-০৮ ১১:৪১; নাম `LSE-live-scan-editing-`)।
