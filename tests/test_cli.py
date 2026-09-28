import subprocess
import sys
import unittest

import egypttranslit


class CommandLineTests(unittest.TestCase):
    def run_cli(
        self, *args: str, input_text: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "egypttranslit", *args],
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_auto_mode_from_arguments(self):
        result = self.run_cli("nTr", "mAat")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "nṯr mꜣꜥt")
        self.assertEqual(result.stderr, "")

    def test_explicit_mdc_mode_from_stdin_preserves_layout(self):
        source = "nTr Htp\n[mAat]"
        result = self.run_cli("--mode", "mdc", input_text=source)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "nṯr ḥtp\n[mꜣꜥt]")

    def test_unicode_mode(self):
        result = self.run_cli("--mode", "unicode", "ȝ", "ʿ", "ỉ")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "ꜣ ꜥ ꞽ")

    def test_version(self):
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(), f"egypttranslit {egypttranslit.__version__}"
        )

    def test_invalid_mode_fails_without_traceback(self):
        result = self.run_cli("--mode", "invalid", "nTr")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
