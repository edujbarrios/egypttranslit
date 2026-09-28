import unicodedata
import unittest
from itertools import product

from egypttranslit import normalize_unicode, parse, parse_mdc

_MDC_ALPHABET = tuple(dict.fromkeys("AaiyjwybpfmnrhHxXzsSqkgtTdD3"))


class ParserContractTests(unittest.TestCase):
    def test_all_short_mdc_tokens_obey_cross_mode_contracts(self):
        for length in range(1, 4):
            for characters in product(_MDC_ALPHABET, repeat=length):
                source = "".join(characters)
                automatic = parse(source)
                explicit = parse_mdc(source)

                self.assertEqual(parse(automatic), automatic, source)
                self.assertEqual(parse_mdc(explicit), explicit, source)
                self.assertEqual(normalize_unicode(automatic), automatic, source)
                self.assertEqual(normalize_unicode(explicit), explicit, source)
                self.assertEqual(parse_mdc(automatic), explicit, source)
                self.assertTrue(unicodedata.is_normalized("NFC", automatic), source)
                self.assertTrue(unicodedata.is_normalized("NFC", explicit), source)

    def test_historical_unicode_variants_commute_with_parsing(self):
        variants = (
            "ȝ",
            "Ȝ",
            "ʿ",
            "ỉ",
            "Ỉ",
            "i\u0313",
            "i\u0357",
            "i\u0486",
            "I\u0313",
            "I\u0357",
            "I\u0486",
        )
        contexts = ("", "n", "mA", "-nTr", "[", "]")

        for variant in variants:
            for prefix, suffix in product(contexts, repeat=2):
                source = f"{prefix}{variant}{suffix}"
                normalized = normalize_unicode(source)

                with self.subTest(source=source):
                    self.assertEqual(normalize_unicode(normalized), normalized)
                    self.assertEqual(parse(normalized), parse(source))
                    self.assertEqual(parse_mdc(normalized), parse_mdc(source))

    def test_sign_code_boundaries_are_protected_exhaustively(self):
        categories = tuple("ABCDEFGHIKLMNOPQRSTUVWXYZ") + (
            "Aa",
            "AA",
            "NL",
            "NU",
            "Ff",
        )
        numbers = (1, 3, 36, 999)
        suffixes = ("", "a", "AB", "abcde")

        for category, number, suffix in product(categories, numbers, suffixes):
            code = f"{category}{number}{suffix}"
            with self.subTest(code=code):
                self.assertEqual(parse(code), code)
                self.assertEqual(parse_mdc(code), code)

    def test_jsesh_prefixed_sign_code_boundaries_are_protected(self):
        prefixes = ("US1", "US22", "US248", "US685")
        categories = ("A", "I", "K", "Z", "Aa", "AA", "NL", "NU")
        numbers = (1, 3, 36, 999)
        suffixes = ("", "a", "AB", "abcde")

        for prefix, category, number, suffix in product(
            prefixes, categories, numbers, suffixes
        ):
            code = f"{prefix}{category}{number}{suffix}"
            with self.subTest(code=code):
                self.assertEqual(parse(code), code)
                self.assertEqual(parse_mdc(code), code)

    def test_sign_code_digit_limit_does_not_overprotect_near_misses(self):
        self.assertEqual(parse_mdc("A1000"), "ꜣ1000")
        self.assertEqual(parse_mdc("D1000"), "ḏ1000")
        self.assertEqual(parse_mdc("T1000"), "ṯ1000")


if __name__ == "__main__":
    unittest.main()
