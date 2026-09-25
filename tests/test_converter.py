import unittest

from egyptological_transliteration_converter_python import convert, parse


class ConverterTests(unittest.TestCase):
    def test_core_mdc_mapping(self):
        self.assertEqual(
            parse("A a H x X S T D"),
            "ꜣ ꜥ ḥ ḫ ẖ š ṯ ḏ",
        )

    def test_example_phrase(self):
        self.assertEqual(
            parse("nTr Htp xpr m mAat"),
            "nṯr ḥtp ḫpr m mꜣꜥt",
        )

    def test_unknown_characters_are_preserved(self):
        source = "nfr 123!?\n𓂀"
        self.assertEqual(parse(source), source)

    def test_existing_unicode_is_preserved(self):
        source = "ꜣ ꜥ ḥ ḫ ẖ š ṯ ḏ"
        self.assertEqual(parse(source), source)

    def test_convert_alias(self):
        self.assertEqual(convert("Htp"), parse("Htp"))

    def test_empty_string(self):
        self.assertEqual(parse(""), "")

    def test_non_string_rejected(self):
        with self.assertRaises(TypeError):
            parse(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
