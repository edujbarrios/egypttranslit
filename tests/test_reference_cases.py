import json
import unittest
from pathlib import Path

from egypttranslit import normalize_unicode, parse, parse_mdc
from egypttranslit.converter import parse_mdc_profiled

_FIXTURE = Path(__file__).with_name("fixtures") / "reference_cases.json"


class ReferenceCaseTests(unittest.TestCase):
    def test_curated_reference_cases(self):
        cases = json.loads(_FIXTURE.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(source=case["source"], mode=case["mode"]):
                mode = case["mode"]
                if mode == "auto":
                    actual = parse(case["source"])
                elif mode == "mdc":
                    actual = parse_mdc(case["source"])
                elif mode == "mdc-legacy":
                    actual = parse_mdc_profiled(
                        case["source"], profile="legacy-diacritics"
                    )
                elif mode == "unicode":
                    actual = normalize_unicode(case["source"])
                else:
                    self.fail(f"unknown fixture mode {mode!r}")
                self.assertEqual(actual, case["expected"])


if __name__ == "__main__":
    unittest.main()
