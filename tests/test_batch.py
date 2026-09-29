import unittest

from egypttranslit.batch import (
    normalize_unicode_many,
    parse_many,
    parse_mdc_many,
    parse_mdc_profiled_many,
)


class BatchConversionTests(unittest.TestCase):
    def test_parse_many_preserves_order(self):
        self.assertEqual(
            parse_many(["nTr mAat", "A taxi on the X axis."]),
            ("nṯr mꜣꜥt", "A taxi on the X axis."),
        )

    def test_parse_mdc_many_converts_multiple_items(self):
        self.assertEqual(
            parse_mdc_many(("nTr Htp", "xpr mAat")),
            ("nṯr ḥtp", "ḫpr mꜣꜥt"),
        )

    def test_profiled_batch_uses_one_profile(self):
        self.assertEqual(
            parse_mdc_profiled_many(["jr qd", "nTr mAat"], profile="gardiner-1957"),
            ("ꞽr ḳd", "nṯr mꜣꜥt"),
        )

    def test_batch_accepts_generators(self):
        source = (text for text in ["nTr", "Htp"])
        self.assertEqual(parse_mdc_many(source), ("nṯr", "ḥtp"))

    def test_unicode_batch(self):
        self.assertEqual(
            normalize_unicode_many(["ȝ ʿ", "ỉ"]),
            ("ꜣ ꜥ", "ꞽ"),
        )

    def test_empty_batch_returns_empty_tuple(self):
        self.assertEqual(parse_mdc_many([]), ())

    def test_single_string_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "iterable of strings"):
            parse_mdc_many("nTr")

    def test_invalid_item_uses_existing_string_validation(self):
        with self.assertRaisesRegex(TypeError, "text must be a string"):
            parse_mdc_many(["nTr", 3])  # type: ignore[list-item]


if __name__ == "__main__":
    unittest.main()
