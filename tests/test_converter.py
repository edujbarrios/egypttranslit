import unittest

from egypttranslit import convert, parse


class ConverterTests(unittest.TestCase):
    def test_core_mdc_mapping(self):
        self.assertEqual(parse("A a H x X S T D"), "ꜣ ꜥ ḥ ḫ ẖ š ṯ ḏ")

    def test_example_phrase(self):
        self.assertEqual(parse("nTr Htp xpr m mAat"), "nṯr ḥtp ḫpr m mꜣꜥt")

    def test_plain_mdc_word_with_only_lowercase_ayin_is_converted(self):
        self.assertEqual(parse("ra"), "rꜥ")

    def test_ordinary_single_words_are_not_mistaken_for_mdc(self):
        for source in ("data", "main", "minimum", "train"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)

    def test_mixed_prose_only_converts_signalled_transliteration(self):
        self.assertEqual(
            parse("The word mAat is often discussed in Egyptology."),
            "The word mꜣꜥt is often discussed in Egyptology.",
        )

    def test_ordinary_mixed_prose_is_not_corrupted(self):
        source = "Example data stays exactly as written."
        self.assertEqual(parse(source), source)

    def test_editorial_punctuation_is_preserved(self):
        self.assertEqual(
            parse("[mAat].nTr-Htp=sn <xpr>"),
            "[mꜣꜥt].nṯr-ḥtp=sn <ḫpr>",
        )

    def test_unbalanced_editorial_marks_do_not_break_parsing(self):
        self.assertEqual(parse("[mAat nTr"), "[mꜣꜥt nṯr")

    def test_alternate_aleph_three_inside_mdc_token(self):
        self.assertEqual(parse("n3"), "nꜣ")

    def test_bare_three_in_prose_is_preserved(self):
        self.assertEqual(parse("Chapter 3 contains data."), "Chapter 3 contains data.")

    def test_ifao_style_unicode_aleph_and_ayin_are_canonicalized(self):
        self.assertEqual(parse("ȝ ʿ"), "ꜣ ꜥ")

    def test_ifao_yod_variant_is_canonicalized(self):
        self.assertEqual(parse("ỉ"), "ꞽ")

    def test_legacy_unicode_yod_sequences_are_canonicalized(self):
        for source in ("i\u0313", "i\u0357", "i\u0486"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), "ꞽ")

    def test_legacy_uppercase_yod_sequences_preserve_case(self):
        for source in ("I\u0313", "I\u0357", "I\u0486"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), "Ꞽ")

    def test_decomposed_unicode_is_normalized(self):
        self.assertEqual(parse("h\u0323"), "ḥ")

    def test_existing_unicode_is_preserved(self):
        source = "ꜣ ꜥ ꞽ ḥ ḫ ẖ š ṯ ḏ ḳ"
        self.assertEqual(parse(source), source)

    def test_unknown_characters_are_preserved(self):
        source = "nfr 123!?\n𓂀"
        self.assertEqual(parse(source), source)

    def test_numbers_do_not_disable_otherwise_mdc_document(self):
        self.assertEqual(parse("ra 2026 nTr"), "rꜥ 2026 nṯr")

    def test_whitespace_and_multiline_text_are_preserved(self):
        source = "nTr\tHtp\n\n  mAat"
        self.assertEqual(parse(source), "nṯr\tḥtp\n\n  mꜣꜥt")

    def test_parse_is_idempotent(self):
        samples = [
            "nTr Htp xpr m mAat",
            "ȝ ʿ ỉ",
            "i\u0357 Htp",
            "The word mAat appears here.",
            "[mAat].nTr-Htp=sn",
            "data",
            "𓂀 nfr",
        ]
        for source in samples:
            with self.subTest(source=source):
                once = parse(source)
                self.assertEqual(parse(once), once)

    def test_convert_alias(self):
        self.assertEqual(convert("Htp"), parse("Htp"))

    def test_empty_string(self):
        self.assertEqual(parse(""), "")

    def test_non_string_rejected(self):
        with self.assertRaises(TypeError):
            parse(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
