"""Canonical anchors — the 5 promoted live pages and the Round 3
database must be UNTOUCHED (read-only SHA checks). The package never
writes under live-paper-prototype/ or to the shared DB.
"""
import hashlib
import os
import unittest

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from helpers import CANONICAL_LIVE_SHAS, R3_DB, R3_DB_SHA, SP, requires_real_fixtures


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@requires_real_fixtures
class TestCanonicalUntouched(unittest.TestCase):
    def test_five_live_pages_byte_identical(self):
        for name, expected in CANONICAL_LIVE_SHAS.items():
            got = _sha(os.path.join(SP, name))
            print(f"  {name}: {got[:16]}...")
            self.assertEqual(got, expected, f"{name} changed!")

    def test_round3_db_unchanged(self):
        got = _sha(R3_DB)
        print(f"  lse_gravora.db: {got[:16]}... (expect 1c065457...)")
        self.assertEqual(got, R3_DB_SHA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
