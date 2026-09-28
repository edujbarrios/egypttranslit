import inspect
import unittest
from typing import get_type_hints

import egypttranslit

_PUBLIC_FUNCTIONS = {
    "convert": egypttranslit.convert,
    "normalize_unicode": egypttranslit.normalize_unicode,
    "parse": egypttranslit.parse,
    "parse_mdc": egypttranslit.parse_mdc,
}


class PublicApiContractTests(unittest.TestCase):
    def test_declared_exports_are_exact_and_stable(self):
        self.assertEqual(
            egypttranslit.__all__,
            ["convert", "normalize_unicode", "parse", "parse_mdc"],
        )

    def test_public_converter_signatures_are_one_string_to_string(self):
        for name, function in _PUBLIC_FUNCTIONS.items():
            signature = inspect.signature(function)
            with self.subTest(function=name):
                self.assertEqual(list(signature.parameters), ["text"])
                parameter = signature.parameters["text"]
                self.assertIs(parameter.kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                self.assertIs(parameter.default, inspect.Parameter.empty)
                self.assertEqual(get_type_hints(function), {"text": str, "return": str})

    def test_all_public_converters_reject_non_strings(self):
        values = (None, b"nTr", 7, 3.14, [], {}, object())
        for name, function in _PUBLIC_FUNCTIONS.items():
            for value in values:
                with (
                    self.subTest(function=name, value_type=type(value).__name__),
                    self.assertRaisesRegex(TypeError, r"^text must be a string$"),
                ):
                    function(value)  # type: ignore[arg-type]

    def test_string_subclasses_are_accepted_and_return_plain_strings(self):
        class ScholarlyText(str):
            pass

        source = ScholarlyText("nTr")
        for name, function in _PUBLIC_FUNCTIONS.items():
            with self.subTest(function=name):
                result = function(source)
                self.assertIs(type(result), str)

    def test_empty_input_is_a_fixed_point(self):
        for name, function in _PUBLIC_FUNCTIONS.items():
            with self.subTest(function=name):
                self.assertEqual(function(""), "")

    def test_lone_surrogates_are_preserved_without_exceptions(self):
        source = chr(0xD800) + "|" + chr(0xDFFF)
        for name, function in _PUBLIC_FUNCTIONS.items():
            with self.subTest(function=name):
                self.assertEqual(function(source), source)

    def test_control_characters_and_line_endings_are_not_rewritten(self):
        prefix = "\x00\x01\t\r\n"
        suffix = "\n\r\x1f\x7f"
        source = f"{prefix}nTr{suffix}"

        self.assertEqual(egypttranslit.parse(source), f"{prefix}nṯr{suffix}")
        self.assertEqual(egypttranslit.convert(source), f"{prefix}nṯr{suffix}")
        self.assertEqual(egypttranslit.parse_mdc(source), f"{prefix}nṯr{suffix}")
        self.assertEqual(egypttranslit.normalize_unicode(source), source)


if __name__ == "__main__":
    unittest.main()
