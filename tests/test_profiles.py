import unittest

from egypttranslit import parse_mdc


class TransliterationProfileTests(unittest.TestCase):
    def test_default_profile_preserves_editorial_alternatives(self):
        self.assertEqual(parse_mdc("jr qd"), "jr qd")

    def test_legacy_diacritics_profile_is_explicit(self):
        self.assertEqual(
            parse_mdc("jr qd mAat", profile="legacy-diacritics"),
            "ꞽr ḳd mꜣꜥt",
        )

    def test_profiles_do_not_rewrite_sign_codes(self):
        self.assertEqual(
            parse_mdc("A1q D36j", profile="legacy-diacritics"),
            "A1q D36j",
        )

    def test_unknown_profile_is_rejected_even_without_tokens(self):
        with self.assertRaisesRegex(ValueError, "unknown transliteration profile"):
            parse_mdc("", profile="unsupported")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
