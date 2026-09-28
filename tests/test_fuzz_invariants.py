import random
import unicodedata
import unittest

from egypttranslit import normalize_unicode, parse, parse_mdc

_SEED = 0xE6A7
_CASES = 4_000
_SENTINEL = "\ue123\U0001f7e3"

_FRAGMENTS = (
    "",
    "nTr",
    "mAat",
    "Htp",
    "xpr",
    "n3",
    "mATH",
    "AT",
    "nTrHtp",
    "n33",
    "A1",
    "D36",
    "T3",
    "Aa1",
    "AA1",
    "NL5",
    "US1A1",
    "US248Aa1",
    "ȝ",
    "Ȝ",
    "ʿ",
    "ỉ",
    "Ỉ",
    "i\u0313",
    "i\u0357",
    "i\u0486",
    "I\u0313",
    "I\u0357",
    "I\u0486",
    "ꜣꜥꞽḥḫẖšṯḏḳ",
    "[()]{}<>-=.:;!?/\\\t\r\n",
    "\U00013000\U00013437\U00013001",
    "\U00013443\ufe00",
    "漢字",
    "العربية",
    "🙂🧪📜",
)

_RANGES = (
    (0x0000, 0x007F),
    (0x0080, 0x024F),
    (0x0300, 0x036F),
    (0x2000, 0x206F),
    (0xD800, 0xDFFF),
    (0xE000, 0xF8FF),
    (0x13000, 0x143FF),
    (0x1F300, 0x1FAFF),
)


def _random_code_point(rng: random.Random) -> str:
    start, end = rng.choice(_RANGES)
    return chr(rng.randint(start, end))


def _random_source(rng: random.Random) -> str:
    parts: list[str] = []
    for _ in range(rng.randint(0, 14)):
        if rng.random() < 0.7:
            parts.append(rng.choice(_FRAGMENTS))
        else:
            parts.append(_random_code_point(rng))
    return "".join(parts)


class DeterministicFuzzInvariantTests(unittest.TestCase):
    def test_mixed_unicode_is_total_nfc_and_idempotent(self):
        rng = random.Random(_SEED)
        converters = (normalize_unicode, parse, parse_mdc)

        for case in range(_CASES):
            source = _random_source(rng)
            for converter in converters:
                result = converter(source)
                with self.subTest(case=case, mode=converter.__name__):
                    self.assertIs(type(result), str)
                    self.assertEqual(unicodedata.normalize("NFC", result), result)
                    self.assertEqual(converter(result), result)

    def test_opaque_sentinels_survive_random_mixed_contexts(self):
        rng = random.Random(_SEED ^ 0x5A5A)

        for case in range(_CASES // 4):
            source = f"{_SENTINEL}{_random_source(rng)}{_SENTINEL}"
            for converter in (normalize_unicode, parse, parse_mdc):
                result = converter(source)
                with self.subTest(case=case, mode=converter.__name__):
                    self.assertEqual(result.count(_SENTINEL), 2)

    def test_large_mixed_document_preserves_structure(self):
        source_line = "A1 nTr D36 Htp ȝ ʿ ỉ \U00013000\U00013437\U00013001\n"
        automatic_line = "A1 nṯr D36 Htp ꜣ ꜥ ꞽ \U00013000\U00013437\U00013001\n"
        explicit_line = "A1 nṯr D36 ḥtp ꜣ ꜥ ꞽ \U00013000\U00013437\U00013001\n"
        source = source_line * 5_000

        self.assertEqual(parse(source), automatic_line * 5_000)
        self.assertEqual(parse_mdc(source), explicit_line * 5_000)
        self.assertEqual(normalize_unicode(source), source.replace("ȝ", "ꜣ").replace("ʿ", "ꜥ").replace("ỉ", "ꞽ"))


if __name__ == "__main__":
    unittest.main()
