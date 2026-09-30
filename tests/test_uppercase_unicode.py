import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc


class UppercaseUnicodeTests(unittest.TestCase):
    def test_historical_uppercase_forms_have_canonical_and_ifao_outputs(self):
        self.assertEqual(normalize_unicode("Ȝ Ỉ"), "Ꜣ Ꞽ")
        self.assertEqual(parse("Ȝ Ỉ"), "Ȝ Ỉ")

    def test_canonical_uppercase_egyptological_unicode_uses_ifao_presentation(self):
        source = "Ꜣ Ꜥ Ꞽ Ḥ Ḫ Š Ṯ Ḏ Ḳ"
        expected_ifao = "Ȝ ʿ Ỉ Ḥ Ḫ Š Ṯ Ḏ Ḳ"
        self.assertEqual(normalize_unicode(source), source)
        self.assertEqual(parse(source), expected_ifao)
        self.assertEqual(parse_mdc(source), expected_ifao)

    def test_uppercase_xh_sequence_is_never_mistaken_for_mdc_h(self):
        source = "H\u0331tp"
        self.assertEqual(parse(source), source)
        self.assertEqual(parse_mdc(source), source)
        self.assertEqual(normalize_unicode(source), source)

    def test_uppercase_xh_is_preserved_inside_mixed_prose(self):
        source = "The form H\u0331tp is already Unicode."
        self.assertEqual(parse(source), source)

    def test_uppercase_unicode_operations_are_idempotent(self):
        samples = [
            "Ȝ Ỉ",
            "Ꜣ Ꜥ Ꞽ Ḥ Ḫ Š Ṯ Ḏ Ḳ",
            "H\u0331tp",
            "The form H\u0331tp is already Unicode.",
        ]
        for source in samples:
            with self.subTest(source=source):
                parsed = parse(source)
                normalized = normalize_unicode(source)
                explicit = parse_mdc(source)
                self.assertEqual(parse(parsed), parsed)
                self.assertEqual(normalize_unicode(normalized), normalized)
                self.assertEqual(parse_mdc(explicit), explicit)


if __name__ == "__main__":
    unittest.main()
