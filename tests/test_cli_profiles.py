import subprocess
import sys
import unittest


class CommandLineProfileTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "egypttranslit", *args],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def test_legacy_profile_in_mdc_mode(self):
        result = self.run_cli(
            "--mode",
            "mdc",
            "--profile",
            "legacy-diacritics",
            "jr",
            "qd",
            "mAat",
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "ꞽr ḳd mꜣꜥt")
        self.assertEqual(result.stderr, "")

    def test_non_default_profile_requires_mdc_mode(self):
        result = self.run_cli("--profile", "legacy-diacritics", "mAat")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--profile requires --mode mdc", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
