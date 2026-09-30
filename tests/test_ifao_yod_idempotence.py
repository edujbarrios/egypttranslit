import unittest

from egypttranslit import parse, parse_mdc


class IfaoYodIdempotenceTests(unittest.TestCase):
    def test_ifao_yod_with_additional_legacy_mark_is_not_reinterpreted(self):
        for source in ("ỉ\u0357", "Ỉ\u0357", "ỉ\u0486", "Ỉ\u0486"):
            with self.subTest(source=source):
                self.assertEqual(parse(parse(source)), parse(source))
                self.assertEqual(parse_mdc(parse_mdc(source)), parse_mdc(source))


if __name__ == "__main__":
    unittest.main()
