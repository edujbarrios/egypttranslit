import re
import unittest
from importlib.metadata import version
from pathlib import Path

import egypttranslit


ROOT = Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    def test_release_versions_are_synchronized(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

        project_match = re.search(
            r'^version\s*=\s*"([^"]+)"\s*$', pyproject, re.MULTILINE
        )
        citation_match = re.search(
            r'^version:\s*"([^"]+)"\s*$', citation, re.MULTILINE
        )
        self.assertIsNotNone(project_match)
        self.assertIsNotNone(citation_match)
        assert project_match is not None
        assert citation_match is not None

        installed = version("egypttranslit")
        self.assertEqual(project_match.group(1), installed)
        self.assertEqual(citation_match.group(1), installed)
        self.assertEqual(egypttranslit.__version__, installed)


if __name__ == "__main__":
    unittest.main()
