import random
import unicodedata
import unittest
from importlib.metadata import version

import egypttranslit
from egypttranslit import convert, normalize_unicode, parse, parse_mdc


class ConverterTests(unittest.TestCase):
    def test_core_mdc_mapping_in_explicit_mode(self):
        self.assertEqual(
            parse_mdc("A a H x X S T D"),
            "ȝ ʿ ḥ ḫ ẖ š ṯ ḏ",
        )

    def test_complete_mdc_example_in_explicit_mode(self):
        self.assertEqual(
            parse_mdc("nTr Htp xpr m mAat"),
            "nṯr ḥtp ḫpr m mȝʿt",
        )

    def test_auto_parse_only_converts_self_signalling_tokens(self):
        self.assertEqual(
            parse("nTr Htp xpr m mAat"),
            "nṯr Htp xpr m mȝʿt",
        )

    def test_ambiguous_lowercase_mdc_is_preserved_by_auto_parse(self):
        self.assertEqual(parse("ra"), "ra")
        self.assertEqual(parse_mdc("ra"), "rʿ")

    def test_plain_x_words_are_not_mistaken_for_mdc(self):
        for source in ("axis", "taxi", "tax", "wax", "xray"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)

    def test_title_case_words_are_not_mistaken_for_mdc(self):
        for source in ("Data", "Train", "Hat", "Sad", "Tax"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)

    def test_one_letter_mdc_shortcuts_are_not_guessed(self):
        source = "A a H x X S T D"
        self.assertEqual(parse(source), source)

    def test_ordinary_single_words_are_not_mistaken_for_mdc(self):
        for source in ("data", "main", "minimum", "train"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)

    def test_multiple_mdc_compatible_ordinary_words_are_not_mistaken_for_mdc(self):
        for source in ("main train", "data main", "train data", "axis data"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), source)

    def test_mixed_prose_only_converts_self_signalling_transliteration(self):
        self.assertEqual(
            parse("The word mAat is often discussed in Egyptology."),
            "The word mȝʿt is often discussed in Egyptology.",
        )
        self.assertEqual(
            parse("A taxi may contain Htp as plain text."),
            "A taxi may contain Htp as plain text.",
        )

    def test_ordinary_mixed_prose_is_not_corrupted(self):
        source = "Example data stays exactly as written on the X axis."
        self.assertEqual(parse(source), source)

    def test_editorial_punctuation_is_preserved_in_explicit_mode(self):
        self.assertEqual(
            parse_mdc("[mAat].nTr-Htp=sn <xpr>"),
            "[mȝʿt].nṯr-ḥtp=sn <ḫpr>",
        )

    def test_auto_parse_does_not_propagate_across_editorial_boundaries(self):
        self.assertEqual(
            parse("[mAat].nTr-Htp=sn <xpr>"),
            "[mȝʿt].nṯr-Htp=sn <xpr>",
        )

    def test_unbalanced_editorial_marks_do_not_break_explicit_parsing(self):
        self.assertEqual(parse_mdc("[mAat nTr"), "[mȝʿt nṯr")

    def test_alternate_aleph_three_inside_mdc_token(self):
        self.assertEqual(parse("n3"), "nȝ")

    def test_bare_three_in_prose_is_preserved(self):
        self.assertEqual(parse("Chapter 3 contains data."), "Chapter 3 contains data.")

    def test_three_does_not_turn_neighbouring_plain_words_into_mdc(self):
        self.assertEqual(parse("n3 data"), "nȝ data")

    def test_ifao_style_unicode_aleph_and_ayin_are_preserved(self):
        self.assertEqual(parse("ȝ ʿ"), "ȝ ʿ")

    def test_ifao_yod_variant_is_preserved(self):
        self.assertEqual(parse("ỉ"), "ỉ")

    def test_legacy_unicode_yod_sequences_are_rendered_as_ifao_yod(self):
        for source in ("i\u0313", "i\u0357", "i\u0486"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), "ỉ")

    def test_legacy_uppercase_yod_sequences_preserve_case(self):
        for source in ("I\u0313", "I\u0357", "I\u0486"):
            with self.subTest(source=source):
                self.assertEqual(parse(source), "Ỉ")

    def test_decomposed_unicode_is_normalized(self):
        self.assertEqual(parse("h\u0323"), "ḥ")

    def test_canonical_unicode_is_rendered_in_default_ifao_style(self):
        source = "ꜣ ꜥ ꞽ ḥ ḫ ẖ š ṯ ḏ ḳ"
        expected = "ȝ ʿ ỉ ḥ ḫ ẖ š ṯ ḏ ḳ"
        self.assertEqual(parse(source), expected)

    def test_unicode_marker_does_not_force_ascii_mdc_conversion(self):
        self.assertEqual(parse("ꜣdata"), "ȝdata")
        self.assertEqual(parse("ȝdata"), "ȝdata")

    def test_unknown_characters_are_preserved(self):
        source = "nfr 123!?\n𓂀"
        self.assertEqual(parse(source), source)

    def test_auto_parse_never_infers_neighbouring_tokens(self):
        self.assertEqual(parse("ra 2026 nTr"), "ra 2026 nṯr")
        self.assertEqual(parse_mdc("ra 2026 nTr"), "rʿ 2026 nṯr")

    def test_whitespace_and_multiline_text_are_preserved(self):
        source = "nTr\tHtp\n\n  mAat"
        self.assertEqual(parse(source), "nṯr\tHtp\n\n  mȝʿt")
        self.assertEqual(parse_mdc(source), "nṯr\tḥtp\n\n  mȝʿt")

    def test_ifao_plain_text_reference_sample_is_stable(self):
        source = (
            "ḏd-ḥr mȝʿ-ḫrw sȝ n ʿnḫ-ḥr sȝ ỉrỉ-pʿt ḥȝtỉ-ʿ wr ʿȝ n mšwš "
            "ḥȝtỉ-ʿỉmỉ-rȝ ḥmw-nṯr n bȝ-nb-ḏw ḏd-ḥr mwt=f nbt pr šp-n-spdt mȝʿ-ḫr"
        )
        self.assertEqual(parse(source), source)
        self.assertEqual(parse_mdc(source), source)

    def test_normalize_unicode_still_returns_canonical_forms(self):
        self.assertEqual(normalize_unicode("ȝ ʿ ỉ"), "ꜣ ꜥ ꞽ")

    def test_parse_is_idempotent(self):
        samples = [
            "nTr Htp xpr m mAat",
            "ȝ ʿ ỉ",
            "i\u0357 Htp",
            "The word mAat appears here.",
            "A taxi on the X axis.",
            "[mAat].nTr-Htp=sn",
            "ra",
            "data",
            "main train",
            "n3 data",
            "ꜣdata",
            "𓂀 nfr",
        ]
        for source in samples:
            with self.subTest(source=source):
                once = parse(source)
                self.assertEqual(parse(once), once)

    def test_deterministic_mixed_input_preserves_parser_invariants(self):
        alphabet = tuple(
            "AaiyjwybpfmnrhHxXzsSqkgtTdD3 maintrainaxis"
            "ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ"
            "[]-_=.,!? \n\t"
        ) + ("𓂀", "\u0313", "\u0357", "\u0486", "\u0331")
        rng = random.Random(20260928)

        for _ in range(3000):
            source = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 60)))
            result = parse(source)
            self.assertEqual(parse(result), result)
            self.assertEqual(unicodedata.normalize("NFC", result), result)

    def test_random_unicode_scalars_preserve_invariants_for_all_modes(self):
        rng = random.Random(20260928)

        def random_scalar() -> str:
            while True:
                value = rng.randrange(0x110000)
                if not 0xD800 <= value <= 0xDFFF:
                    return chr(value)

        for _ in range(1500):
            source = "".join(random_scalar() for _ in range(rng.randint(0, 32)))
            for converter in (parse, parse_mdc, normalize_unicode):
                result = converter(source)
                self.assertEqual(converter(result), result)
                self.assertEqual(unicodedata.normalize("NFC", result), result)

    def test_package_version_matches_distribution_metadata(self):
        self.assertEqual(egypttranslit.__version__, version("egypttranslit"))

    def test_convert_alias(self):
        self.assertEqual(convert("nTr mAat"), parse("nTr mAat"))

    def test_empty_string(self):
        self.assertEqual(parse(""), "")

    def test_non_string_rejected(self):
        with self.assertRaises(TypeError):
            parse(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
