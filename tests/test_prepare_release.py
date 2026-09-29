import tempfile
import unittest
from pathlib import Path

from scripts.prepare_release import (
    parse_version,
    prepare_release,
    update_changelog,
    update_citation,
    update_pyproject,
)


class PrepareReleaseTests(unittest.TestCase):
    def test_parse_version_accepts_final_release(self):
        self.assertEqual(parse_version("1.2.3"), (1, 2, 3))

    def test_parse_version_rejects_non_final_or_ambiguous_versions(self):
        for value in ("1.2", "v1.2.3", "1.2.3rc1", "01.2.3"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "X.Y.Z"):
                    parse_version(value)

    def test_text_updates_are_targeted(self):
        self.assertEqual(
            update_pyproject('[project]\nversion = "0.9.0"\n', "0.10.0"),
            '[project]\nversion = "0.10.0"\n',
        )
        self.assertEqual(
            update_citation('version: "0.9.0"\n', "0.10.0"),
            'version: "0.10.0"\n',
        )
        self.assertEqual(
            update_changelog(
                "# Changelog\n\n## 0.9.0\n\n- Old.\n",
                "0.10.0",
                "- New.",
            ),
            "# Changelog\n\n## 0.10.0\n\n- New.\n\n## 0.9.0\n\n- Old.\n",
        )

    def test_prepare_release_updates_all_synchronized_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                '[project]\nversion = "0.9.0"\n', encoding="utf-8"
            )
            (root / "CITATION.cff").write_text(
                'version: "0.9.0"\n', encoding="utf-8"
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.9.0\n\n- Old.\n", encoding="utf-8"
            )

            prepare_release(root, "0.10.0", "- New release.")

            self.assertIn(
                'version = "0.10.0"',
                (root / "pyproject.toml").read_text(encoding="utf-8"),
            )
            self.assertIn(
                'version: "0.10.0"',
                (root / "CITATION.cff").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "## 0.10.0\n\n- New release.",
                (root / "CHANGELOG.md").read_text(encoding="utf-8"),
            )

    def test_prepare_release_rejects_non_increasing_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                '[project]\nversion = "0.9.0"\n', encoding="utf-8"
            )
            (root / "CITATION.cff").write_text(
                'version: "0.9.0"\n', encoding="utf-8"
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.9.0\n\n- Old.\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "must be greater"):
                prepare_release(root, "0.9.0", "- Duplicate.")


if __name__ == "__main__":
    unittest.main()
