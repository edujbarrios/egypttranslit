import unicodedata
import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc


class SymbolConversionContractTests(unittest.TestCase):
    def test_every_supported_mdc_shortcut_has_an_explicit_contract(self):
        cases = {
            "A": "ꜣ",
            "a": "ꜥ",
            "H": "ḥ",
            "x": "ḫ",
            "X": "ẖ",
            "S": "š",
            "T": "ṯ",
            "D": "ḏ",
            "3": "ꜣ",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(parse_mdc(source), expected)

    def test_modern_unicode_transliteration_is_already_a_fixed_point(self):
        source = "ꜣ ꜥ ꞽ ḥ ḫ ẖ š ṯ ḏ ḳ"
        self.assertEqual(parse(source), source)
        self.assertEqual(parse_mdc(source), source)
        self.assertEqual(normalize_unicode(source), source)

    def test_multidigit_numbers_are_never_treated_as_mdc_aleph(self):
        for source in ("10", "30", "300", "2026"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)
                self.assertEqual(parse_mdc(source), source)

    def test_gardiner_and_jsesh_identifiers_are_opaque(self):
        for source in ("A1", "D36", "T3", "Aa1", "NL5", "US1A1"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)
                self.assertEqual(parse_mdc(source), source)

    def test_hieroglyphs_and_format_controls_are_opaque_unicode(self):
        source = "𓀀\U00013430𓂀\U00013431"
        self.assertEqual(parse(source), source)
        self.assertEqual(parse_mdc(source), source)
        self.assertEqual(normalize_unicode(source), source)

    def test_unrelated_combining_marks_are_preserved_under_nfc(self):
        source = "n\u0301 r\u0323 m\u0304"
        expected = unicodedata.normalize("NFC", source)
        self.assertEqual(parse(source), expected)
        self.assertEqual(parse_mdc(source), expected)
        self.assertEqual(normalize_unicode(source), expected)

    def test_unrelated_scripts_and_emoji_are_opaque(self):
        source = "Ελληνικά العربية 漢字 🐍📜"
        self.assertEqual(parse(source), source)
        self.assertEqual(parse_mdc(source), source)
        self.assertEqual(normalize_unicode(source), source)

    def test_punctuation_and_layout_are_preserved_around_conversion(self):
        source = "[nTr]:mAat*Htp!"
        self.assertEqual(parse_mdc(source), "[nṯr]:mꜣꜥt*ḥtp!")


if __name__ == "__main__":
    unittest.main()
