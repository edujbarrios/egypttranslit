import unittest

from egypttranslit.diagnostics import ConversionResult, analyze, validate


class DiagnosticTests(unittest.TestCase):
    def test_analyze_reports_conversion(self):
        result = analyze("mAat", mode="mdc")
        self.assertIsInstance(result, ConversionResult)
        self.assertEqual(result.text, "mȝʿt")
        self.assertTrue(result.changed)
        self.assertEqual(result.detected, "mdc")
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.warnings, ())

    def test_analyze_reports_unicode_input(self):
        result = analyze("nṯr mꜣꜥt", mode="unicode")
        self.assertEqual(result.detected, "unicode")
        self.assertEqual(result.confidence, 1.0)

    def test_analyze_reports_uppercase_xh_as_unicode(self):
        result = analyze("H\u0331", mode="unicode")
        self.assertEqual(result.text, "H\u0331")
        self.assertEqual(result.detected, "unicode")
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.warnings, ())

    def test_analyze_reports_ambiguous_plain_ascii(self):
        result = analyze("maat", mode="auto")
        self.assertEqual(result.detected, "ambiguous")
        self.assertEqual(result.confidence, 0.0)

    def test_analyze_reports_non_transliteration_input(self):
        result = analyze("☀️ — 𓀀", mode="auto")
        self.assertEqual(result.detected, "none")
        self.assertEqual(result.confidence, 1.0)

    def test_analyze_reports_mixed_encoding_token(self):
        result = analyze("mAꜥt", mode="mdc")
        self.assertEqual(result.text, "mȝʿt")
        self.assertEqual(result.detected, "mixed")
        self.assertEqual(result.confidence, 1.0)
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
        result = analyze("A1q D36j", mode="mdc", profile="gardiner-1957")
        self.assertEqual(result.warnings, ())

    def test_confidence_is_documented_heuristic_not_mode_assertion(self):
        result = analyze("ordinary", mode="mdc")
        self.assertEqual(result.detected, "ambiguous")
        self.assertEqual(result.confidence, 0.0)

    def test_unknown_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown conversion mode"):
            analyze("nTr", mode="invalid")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
