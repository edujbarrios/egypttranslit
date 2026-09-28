import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc


class ExplicitModeTests(unittest.TestCase):
    def test_parse_mdc_converts_ambiguous_ascii_when_caller_knows_format(self):
        self.assertEqual(parse("main train"), "main train")
        self.assertEqual(parse_mdc("main train"), "mꜥin trꜥin")

    def test_parse_mdc_preserves_unknown_characters_and_layout(self):
        self.assertEqual(parse_mdc("nTr!?\n𓂀 Htp"), "nṯr!?\n𓂀 ḥtp")

    def test_parse_mdc_converts_known_shortcuts_next_to_unknown_characters(self):
        self.assertEqual(parse_mdc("v3 Htp"), "vꜣ ḥtp")
        self.assertEqual(parse_mdc("fooAbar"), "fooꜣbꜥr")

    def test_parse_mdc_preserves_multi_digit_numbers(self):
        for source in ("12", "33", "123", "2023", "1000"):
            with self.subTest(source=source):
                self.assertEqual(parse_mdc(source), source)

    def test_parse_mdc_still_accepts_three_as_aleph_in_transliteration(self):
        self.assertEqual(parse_mdc("3"), "ꜣ")
        self.assertEqual(parse_mdc("n3"), "nꜣ")
        self.assertEqual(parse_mdc("3b"), "ꜣb")

    def test_parse_mdc_preserves_uppercase_xh_unicode_sequence(self):
        self.assertEqual(parse_mdc("H\u0331"), "H\u0331")

    def test_parse_mdc_does_not_guess_editorial_j_or_q(self):
        self.assertEqual(parse_mdc("j q"), "j q")

    def test_normalize_unicode_never_interprets_ascii_mdc_shortcuts(self):
        self.assertEqual(normalize_unicode("A a H x X S T D"), "A a H x X S T D")

    def test_normalize_unicode_repairs_verified_historical_forms(self):
        self.assertEqual(normalize_unicode("ȝ ʿ ỉ"), "ꜣ ꜥ ꞽ")
        self.assertEqual(normalize_unicode("i\u0357 I\u0486"), "ꞽ Ꞽ")

    def test_explicit_modes_reject_non_strings(self):
        with self.assertRaises(TypeError):
            parse_mdc(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            normalize_unicode(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
