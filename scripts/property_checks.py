"""Property-based checks for conversion invariants.

Run with: python scripts/property_checks.py
"""

from __future__ import annotations

import unicodedata
import unittest

from hypothesis import given, settings
from hypothesis import strategies as st

from egypttranslit import normalize_unicode, parse, parse_mdc


class ConversionPropertyTests(unittest.TestCase):
    @settings(max_examples=1000, deadline=None)
    @given(st.text())
    def test_auto_parse_is_idempotent_and_nfc(self, source: str) -> None:
        converted = parse(source)
        self.assertEqual(parse(converted), converted)
        self.assertEqual(unicodedata.normalize("NFC", converted), converted)

    @settings(max_examples=1000, deadline=None)
    @given(st.text())
    def test_explicit_mdc_is_idempotent_and_nfc(self, source: str) -> None:
        converted = parse_mdc(source)
        self.assertEqual(parse_mdc(converted), converted)
        self.assertEqual(unicodedata.normalize("NFC", converted), converted)

    @settings(max_examples=1000, deadline=None)
    @given(st.text())
    def test_unicode_normalization_is_idempotent_and_nfc(self, source: str) -> None:
        converted = normalize_unicode(source)
        self.assertEqual(normalize_unicode(converted), converted)
        self.assertEqual(unicodedata.normalize("NFC", converted), converted)


if __name__ == "__main__":
    unittest.main()
