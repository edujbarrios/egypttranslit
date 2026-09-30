import unittest

from egypttranslit import parse_mdc
from egypttranslit.converter import parse_mdc_profiled
from egypttranslit.profiles import get_profile_info, list_profile_info


class TransliterationProfileTests(unittest.TestCase):
    def test_default_profile_uses_ifao_plain_text_and_preserves_j_q(self):
        self.assertEqual(parse_mdc("jr qd mAat"), "jr qd mȝʿt")

    def test_explicit_ifao_profile_matches_default(self):
        source = "jr qd mAat ỉrỉ"
        self.assertEqual(
            parse_mdc_profiled(source, profile="ifao"),
            parse_mdc(source),
        )

    def test_unicode_canonical_profile_reproduces_previous_default(self):
        self.assertEqual(
            parse_mdc_profiled("jr qd mAat", profile="unicode-canonical"),
            "jr qd mꜣꜥt",
        )

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
            parse_mdc_profiled("A1q D36j", profile="ifao"),
            "A1q D36j",
        )
        self.assertEqual(
            parse_mdc_profiled("A1q D36j", profile="gardiner-1957"),
            "A1q D36j",
        )

    def test_profile_metadata_exposes_ifao_mapping_source_and_alias(self):
        default = get_profile_info("default")
        ifao = get_profile_info("ifao")
        self.assertEqual(default.alias_of, "ifao")
        self.assertEqual(default.mapping, ifao.mapping)
        self.assertEqual(default.source, ifao.source)
        self.assertIn(("ꜣ", "ȝ"), ifao.mapping)
        self.assertIn(("ꜥ", "ʿ"), ifao.mapping)
        self.assertIn(("ꞽ", "ỉ"), ifao.mapping)
        self.assertIsNone(ifao.alias_of)
        self.assertIsNotNone(ifao.source)
        self.assertIn("IFAO", ifao.source or "")

    def test_profile_metadata_exposes_gardiner_mapping(self):
        gardiner = get_profile_info("gardiner-1957")
        self.assertEqual(gardiner.name, "gardiner-1957")
        self.assertEqual(gardiner.mapping, (("j", "ꞽ"), ("q", "ḳ")))
        self.assertIsNone(gardiner.alias_of)
        self.assertIsNotNone(gardiner.source)
        self.assertIn("UAX #57", gardiner.source or "")

        legacy = get_profile_info("legacy-diacritics")
        self.assertEqual(legacy.alias_of, "gardiner-1957")
        self.assertEqual(legacy.mapping, gardiner.mapping)
        self.assertEqual(legacy.source, gardiner.source)

    def test_profile_metadata_listing_has_stable_order(self):
        self.assertEqual(
            tuple(info.name for info in list_profile_info()),
            (
                "default",
                "ifao",
                "unicode-canonical",
                "gardiner-1957",
                "legacy-diacritics",
            ),
        )

    def test_unknown_profile_is_rejected_even_without_tokens(self):
        with self.assertRaisesRegex(ValueError, "unknown transliteration profile"):
            parse_mdc_profiled("", profile="unsupported")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "unknown transliteration profile"):
            get_profile_info("unsupported")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
