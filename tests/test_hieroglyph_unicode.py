"""Regression contracts for encoded Egyptian hieroglyph data.

Unicode references:
- Egyptian Hieroglyphs: U+13000..U+1342F
- Egyptian Hieroglyph Format Controls: U+13430..U+1345F
- Egyptian Hieroglyphs Extended-A: U+13460..U+143FF
"""

import unicodedata
import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc

_EGYPTIAN_RANGES = (
    range(0x13000, 0x13430),
    range(0x13430, 0x13460),
    range(0x13460, 0x14400),
)


class HieroglyphUnicodeTests(unittest.TestCase):
    def test_every_egyptian_block_code_point_is_opaque_to_all_modes(self):
        for code_points in _EGYPTIAN_RANGES:
            for code_point in code_points:
                source = chr(code_point)
                for converter in (normalize_unicode, parse, parse_mdc):
                    with self.subTest(
                        code_point=f"U+{code_point:05X}", mode=converter.__name__
                    ):
                        self.assertEqual(converter(source), source)

    def test_format_control_sequences_survive_next_to_transliteration(self):
        hieroglyph_sequence = (
            "\U00013000"
            "\U00013437"
            "\U00013001"
            "\U00013430"
            "\U00013002"
            "\U00013438"
            "\U00013431"
            "\U00013003"
        )
        source = f"{hieroglyph_sequence} nTr Htp"

        self.assertEqual(parse(source), f"{hieroglyph_sequence} nṯr Htp")
        self.assertEqual(parse_mdc(source), f"{hieroglyph_sequence} nṯr ḥtp")
        self.assertEqual(normalize_unicode(source), source)

    def test_lost_sign_variation_sequences_are_preserved(self):
        source = "".join(
            chr(code_point) + "\ufe00" for code_point in range(0x13443, 0x13447)
        )

        for converter in (normalize_unicode, parse, parse_mdc):
            with self.subTest(mode=converter.__name__):
                self.assertEqual(converter(source), source)
                self.assertEqual(converter(converter(source)), source)

    def test_damage_modifiers_and_mirror_control_remain_nfc(self):
        source = (
            "\U00013000\U00013440"
            "\U00013001\U00013447"
            "\U00013002\U0001344b"
            "\U00013003\U00013455"
        )

        for converter in (normalize_unicode, parse, parse_mdc):
            result = converter(source)
            with self.subTest(mode=converter.__name__):
                self.assertEqual(result, source)
                self.assertTrue(unicodedata.is_normalized("NFC", result))


if __name__ == "__main__":
    unittest.main()
