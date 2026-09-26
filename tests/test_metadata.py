import re
import unittest
from importlib.metadata import version
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MetadataTests(unittest.TestCase):
    def test_citation_version_matches_installed_package(self):
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        match = re.search(r'^version:\s*"([^"]+)"\s*$', citation, re.MULTILINE)
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.group(1), version("egypttranslit"))


if __name__ == "__main__":
    unittest.main()
