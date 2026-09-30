import unicodedata
import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc

_IFAO_FROM_CANONICAL = str.maketrans(
    {
        "Ꜣ": "Ȝ",
        "ꜣ": "ȝ",
        "Ꜥ": "ʿ",
        "ꜥ": "ʿ",
        "Ꞽ": "Ỉ",
        "ꞽ": "ỉ",
    }
)


class UnicodeContractTests(unittest.TestCase):
    def test_supported_canonical_characters_have_explicit_output_contracts(self):
        canonical = "ꜢꜣꜤꜥꞼꞽḤḥḪḫẖŠšṮṯḎḏḲḳ"
        for character in canonical:
            with self.subTest(character=character, codepoint=f"U+{ord(character):04X}"):
                self.assertEqual(normalize_unicode(character), character)
                expected_ifao = character.translate(_IFAO_FROM_CANONICAL)
                self.assertEqual(parse(character), expected_ifao)
                self.assertEqual(parse_mdc(character), expected_ifao)

    def test_every_canonical_decomposition_round_trips_to_expected_output(self):
        canonical = "ꞼꞽḤḥḪḫẖŠšṮṯḎḏḲḳ"
        for character in canonical:
            decomposed = unicodedata.normalize("NFD", character)
            with self.subTest(
                character=character,
                decomposition=[f"U+{ord(item):04X}" for item in decomposed],
            ):
                self.assertEqual(normalize_unicode(decomposed), character)
                expected_ifao = character.translate(_IFAO_FROM_CANONICAL)
                self.assertEqual(parse(decomposed), expected_ifao)
                self.assertEqual(parse_mdc(decomposed), expected_ifao)

    def test_uppercase_h_with_line_below_stays_atomic(self):
        uppercase_xh = "H\u0331"
        self.assertEqual(unicodedata.normalize("NFC", uppercase_xh), uppercase_xh)
        self.assertEqual(normalize_unicode(uppercase_xh), uppercase_xh)
        self.assertEqual(parse(uppercase_xh), uppercase_xh)
        self.assertEqual(parse_mdc(uppercase_xh), uppercase_xh)

    def test_verified_historical_aliases_have_canonical_and_ifao_outputs(self):
        aliases = {
            "ȝ": ("ꜣ", "ȝ"),
            "Ȝ": ("Ꜣ", "Ȝ"),
            "ʿ": ("ꜥ", "ʿ"),
            "ỉ": ("ꞽ", "ỉ"),
            "Ỉ": ("Ꞽ", "Ỉ"),
            "i\u0313": ("ꞽ", "ỉ"),
            "i\u0357": ("ꞽ", "ỉ"),
            "i\u0486": ("ꞽ", "ỉ"),
            "I\u0313": ("Ꞽ", "Ỉ"),
            "I\u0357": ("Ꞽ", "Ỉ"),
            "I\u0486": ("Ꞽ", "Ỉ"),
        }
        for source, (canonical, ifao) in aliases.items():
            with self.subTest(source=source):
                self.assertEqual(normalize_unicode(source), canonical)
                self.assertEqual(parse(source), ifao)
                self.assertEqual(parse_mdc(source), ifao)

    def test_legacy_yod_survives_additional_combining_marks(self):
        cases = {
            "i\u0323\u0313": ("ꞽ\u0323", "ỉ\u0323"),
            "i\u0313\u0323": ("ꞽ\u0323", "ỉ\u0323"),
            "i\u0301\u0357": ("ꞽ\u0301", "ỉ\u0301"),
            "I\u0323\u0486": ("Ꞽ\u0323", "Ỉ\u0323"),
        }
        for source, (canonical, ifao) in cases.items():
            canonical = unicodedata.normalize("NFC", canonical)
            ifao = unicodedata.normalize("NFC", ifao)
            with self.subTest(source=source, operation="normalize_unicode"):
                result = normalize_unicode(source)
                self.assertEqual(result, canonical)
                self.assertTrue(unicodedata.is_normalized("NFC", result))
            for operation in (parse, parse_mdc):
                with self.subTest(source=source, operation=operation.__name__):
                    result = operation(source)
                    self.assertEqual(result, ifao)
                    self.assertTrue(unicodedata.is_normalized("NFC", result))

    def test_multiple_legacy_yod_marks_are_preserved_without_guessing(self):
        source = "i\u0313\u0357"
        expected = unicodedata.normalize("NFC", source)
        for operation in (normalize_unicode, parse, parse_mdc):
            with self.subTest(operation=operation.__name__):
                self.assertEqual(operation(source), expected)

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
