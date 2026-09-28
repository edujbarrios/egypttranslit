import unicodedata
import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc


class UnicodeContractTests(unittest.TestCase):
    def test_supported_canonical_characters_are_stable(self):
        canonical = "ꜢꜣꜤꜥꞼꞽḤḥḪḫẖŠšṮṯḎḏḲḳ"
        for character in canonical:
            with self.subTest(character=character, codepoint=f"U+{ord(character):04X}"):
                self.assertEqual(normalize_unicode(character), character)
                self.assertEqual(parse(character), character)
                self.assertEqual(parse_mdc(character), character)

    def test_every_canonical_decomposition_round_trips_to_nfc(self):
        canonical = "ꞼꞽḤḥḪḫẖŠšṮṯḎḏḲḳ"
        for character in canonical:
            decomposed = unicodedata.normalize("NFD", character)
            with self.subTest(
                character=character,
                decomposition=[f"U+{ord(item):04X}" for item in decomposed],
            ):
                self.assertEqual(normalize_unicode(decomposed), character)
                self.assertEqual(parse(decomposed), character)
                self.assertEqual(parse_mdc(decomposed), character)

    def test_uppercase_h_with_line_below_stays_atomic(self):
        uppercase_xh = "H\u0331"
        self.assertEqual(unicodedata.normalize("NFC", uppercase_xh), uppercase_xh)
        self.assertEqual(normalize_unicode(uppercase_xh), uppercase_xh)
        self.assertEqual(parse(uppercase_xh), uppercase_xh)
        self.assertEqual(parse_mdc(uppercase_xh), uppercase_xh)

    def test_verified_historical_aliases_reach_the_same_canonical_forms(self):
        aliases = {
            "ȝ": "ꜣ",
            "Ȝ": "Ꜣ",
            "ʿ": "ꜥ",
            "ỉ": "ꞽ",
            "Ỉ": "Ꞽ",
            "i\u0313": "ꞽ",
            "i\u0357": "ꞽ",
            "i\u0486": "ꞽ",
            "I\u0313": "Ꞽ",
            "I\u0357": "Ꞽ",
            "I\u0486": "Ꞽ",
        }
        for source, expected in aliases.items():
            with self.subTest(source=source):
                self.assertEqual(normalize_unicode(source), expected)
                self.assertEqual(parse(source), expected)
                self.assertEqual(parse_mdc(source), expected)

    def test_output_is_nfc_for_combining_mark_contexts(self):
        sources = (
            "h\u0323tp",
            "h\u032exr",
            "s\u030cn",
            "t\u0331n",
            "d\u0331d",
            "q\u0323b",
        )
        for source in sources:
            with self.subTest(source=source):
                for operation in (normalize_unicode, parse, parse_mdc):
                    result = operation(source)
                    self.assertTrue(unicodedata.is_normalized("NFC", result))


if __name__ == "__main__":
    unittest.main()
