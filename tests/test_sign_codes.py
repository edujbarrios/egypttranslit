import unittest

from egypttranslit import parse, parse_mdc


class SignCodeTests(unittest.TestCase):
    def test_standard_sign_codes_are_preserved_in_all_parsing_modes(self):
        codes = (
            "A1",
            "D36",
            "T3",
            "X1",
            "S29",
            "Aa1",
            "AA1",
            "NL5",
            "NU10",
            "Ff1",
            "A1a",
            "D36AB",
        )
        for code in codes:
            with self.subTest(code=code):
                self.assertEqual(parse(code), code)
                self.assertEqual(parse_mdc(code), code)

    def test_jsesh_extended_sign_codes_are_preserved(self):
        codes = (
            "US1A1",
            "US22D36",
            "US248Aa1",
            "US685NL5",
        )
        for code in codes:
            with self.subTest(code=code):
                self.assertEqual(parse(code), code)
                self.assertEqual(parse_mdc(code), code)

    def test_sign_codes_and_transliteration_can_coexist(self):
        source = "A1-nTr-D36-Htp-T3"
        self.assertEqual(parse(source), "A1-nṯr-D36-Htp-T3")
        self.assertEqual(parse_mdc(source), "A1-nṯr-D36-ḥtp-T3")

    def test_sign_code_protection_does_not_disable_aleph_three_shortcut(self):
        self.assertEqual(parse("n3"), "nꜣ")
        self.assertEqual(parse_mdc("n3"), "nꜣ")

    def test_sign_code_with_editorial_punctuation_keeps_layout(self):
        source = "[A1]:D36=T3; nTr"
        self.assertEqual(parse_mdc(source), "[A1]:D36=T3; nṯr")


if __name__ == "__main__":
    unittest.main()
