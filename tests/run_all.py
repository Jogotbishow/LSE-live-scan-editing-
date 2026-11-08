"""Run the whole LSE engine test suite.

Usage (from lse-opensource/):
  <scan-paper venv>/bin/python tests/run_all.py [--fast]

--fast skips the slow suites (test_fontfix Playwright checks and
test_multipage full-document runs); use it for a quick smoke check.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

FAST_SKIP = {"test_fontfix", "test_multipage"}


def main():
    fast = "--fast" in sys.argv
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in sorted(os.listdir(HERE)):
        if name.startswith("test_") and name.endswith(".py"):
            mod = name[:-3]
            if fast and mod in FAST_SKIP:
                print(f"SKIP (fast): {mod}")
                continue
            suite.addTests(loader.loadTestsFromName(mod))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print(f"\n{'=' * 60}\n"
          f"tests run: {result.testsRun}, failures: {len(result.failures)}, "
          f"errors: {len(result.errors)}, skipped: {len(result.skipped)}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
