import unittest

from egypttranslit import parse_mdc
from egypttranslit.converter import parse_mdc_profiled


class TransliterationProfileTests(unittest.TestCase):
    def test_default_profile_preserves_editorial_alternatives(self):
        self.assertEqual(parse_mdc("jr qd"), "jr qd")

    def test_gardiner_1957_profile_is_explicit(self):
        self.assertEqual(
            parse_mdc_profiled("jr qd mAat", profile="gardiner-1957"),
            "ꞽr ḳd mꜣꜥt",
        )

    def test_legacy_diacritics_remains_backward_compatible_alias(self):
        source = "jr qd mAat"
        self.assertEqual(
            parse_mdc_profiled(source, profile="legacy-diacritics"),
            parse_mdc_profiled(source, profile="gardiner-1957"),
        )

    def test_profiles_do_not_rewrite_sign_codes(self):
        self.assertEqual(
            parse_mdc_profiled("A1q D36j", profile="gardiner-1957"),
            "A1q D36j",
        )

    def test_unknown_profile_is_rejected_even_without_tokens(self):
        with self.assertRaisesRegex(ValueError, "unknown transliteration profile"):
            parse_mdc_profiled("", profile="unsupported")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
