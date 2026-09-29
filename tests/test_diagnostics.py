import unittest

from egypttranslit import ConversionResult, analyze, validate


class DiagnosticTests(unittest.TestCase):
    def test_analyze_reports_conversion(self):
        result = analyze("mAat", mode="mdc")
        self.assertIsInstance(result, ConversionResult)
        self.assertEqual(result.text, "mꜣꜥt")
        self.assertTrue(result.changed)
        self.assertEqual(result.warnings, ())

    def test_analyze_reports_mixed_encoding_token(self):
        result = analyze("mAꜥt", mode="mdc")
        self.assertEqual(result.text, "mꜣꜥt")
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("mixed ASCII/Unicode", result.warnings[0])

    def test_validate_rejects_mixed_encoding_token(self):
        with self.assertRaisesRegex(ValueError, "mixed ASCII/Unicode"):
            validate("mAꜥt")

    def test_validate_returns_result_for_clean_input(self):
        result = validate("nTr Htp")
        self.assertEqual(result.text, "nṯr ḥtp")
        self.assertEqual(result.warnings, ())

    def test_sign_codes_are_not_reported_as_mixed(self):
        result = analyze("A1q D36j", mode="mdc", profile="legacy-diacritics")
        self.assertEqual(result.warnings, ())

    def test_unknown_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown conversion mode"):
            analyze("nTr", mode="invalid")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
