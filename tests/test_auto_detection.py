import unittest

from egypttranslit import parse, parse_mdc


class AutomaticDetectionTests(unittest.TestCase):
    def test_single_internal_marker_remains_auto_convertible(self):
        cases = {
            "nTr": "nṯr",
            "mAat": "mꜣꜥt",
            "n3": "nꜣ",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(parse(source), expected)
                self.assertEqual(parse_mdc(source), expected)

    def test_multiple_strong_markers_are_preserved_by_auto_mode(self):
        cases = {
            "mATH": "mꜣṯḥ",
            "nTrHtp": "nṯrḥtp",
            "n33": "nꜣꜣ",
            "AT": "ꜣṯ",
        }
        for source, explicit in cases.items():
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)
                self.assertEqual(parse_mdc(source), explicit)

    def test_leading_marker_alone_is_not_enough_for_auto_mode(self):
        cases = {
            "Htp": "ḥtp",
            "Amun": "ꜣmun",
            "3n": "ꜣn",
        }
        for source, explicit in cases.items():
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)
                self.assertEqual(parse_mdc(source), explicit)

    def test_leading_and_internal_markers_are_ambiguous_in_auto_mode(self):
        cases = {
            "HTp": "ḥṯp",
            "AnTr": "ꜣnṯr",
            "SxD": "šḫḏ",
        }
        for source, explicit in cases.items():
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)
                self.assertEqual(parse_mdc(source), explicit)


if __name__ == "__main__":
    unittest.main()
