"""Property-based checks for conversion invariants.

Run with: python scripts/property_checks.py
"""

from __future__ import annotations

import unicodedata
import unittest

from hypothesis import given, settings, strategies as st

from egypttranslit import normalize_unicode, parse, parse_mdc


@settings(max_examples=1000, deadline=None)
class ConversionPropertyTests(unittest.TestCase):
    @given(st.text())
    def test_auto_parse_is_idempotent_and_nfc(self, source: str) -> None:
        converted = parse(source)
        self.assertEqual(parse(converted), converted)
        self.assertEqual(unicodedata.normalize("NFC", converted), converted)

    @given(st.text())
    def test_explicit_mdc_is_idempotent_and_nfc(self, source: str) -> None:
        converted = parse_mdc(source)
        self.assertEqual(parse_mdc(converted), converted)
        self.assertEqual(unicodedata.normalize("NFC", converted), converted)

    @given(st.text())
    def test_unicode_normalization_is_idempotent_and_nfc(self, source: str) -> None:
        converted = normalize_unicode(source)
        self.assertEqual(normalize_unicode(converted), converted)
        self.assertEqual(unicodedata.normalize("NFC", converted), converted)


if __name__ == "__main__":
    unittest.main()
