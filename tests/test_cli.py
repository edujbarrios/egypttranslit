import io
import subprocess
import sys
import unittest
from unittest.mock import patch

import egypttranslit
from egypttranslit import __main__ as cli


class _BrokenPipeOutput:
    def __init__(self) -> None:
        self.closed = False

    def write(self, text: str) -> int:
        raise BrokenPipeError

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True


class _OSErrorInput:
    def read(self) -> str:
        raise OSError("input unavailable")


class _OSErrorOutput:
    def write(self, text: str) -> int:
        raise OSError("output unavailable")

    def flush(self) -> None:
        pass


class CommandLineTests(unittest.TestCase):
    def run_cli(
        self, *args: str, input_text: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "egypttranslit", *args],
            input=input_text,
            text=True,
            encoding="utf-8",
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

    def test_unicode_mode_reads_utf8_stdin(self):
        source = "ȝ ʿ ỉ\nḫpr"
        result = self.run_cli("--mode", "unicode", input_text=source)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "ꜣ ꜥ ꞽ\nḫpr")

    def test_invalid_utf8_stdin_fails_cleanly(self):
        result = subprocess.run(
            [sys.executable, "-m", "egypttranslit", "--mode", "unicode"],
            input=b"\xff",
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        stderr = result.stderr.decode("utf-8")
        self.assertIn("Unicode input/output error", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_os_error_reading_stdin_fails_cleanly(self):
        stderr = io.StringIO()
        with (
            patch.object(sys, "stdin", _OSErrorInput()),
            patch.object(sys, "stderr", stderr),
        ):
            returncode = cli.main(["--mode", "mdc"])
        self.assertEqual(returncode, 2)
        self.assertIn("I/O error: input unavailable", stderr.getvalue())

    def test_os_error_writing_stdout_fails_cleanly(self):
        stderr = io.StringIO()
        with (
            patch.object(sys, "stdout", _OSErrorOutput()),
            patch.object(sys, "stderr", stderr),
        ):
            returncode = cli.main(["nTr"])
        self.assertEqual(returncode, 2)
        self.assertIn("I/O error: output unavailable", stderr.getvalue())

    def test_broken_pipe_is_a_clean_pipeline_termination(self):
        output = _BrokenPipeOutput()
        with patch.object(sys, "stdout", output):
            returncode = cli.main(["nTr"])
        self.assertEqual(returncode, 0)
        self.assertTrue(output.closed)

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
