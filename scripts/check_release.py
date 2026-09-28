"""Fail fast when release metadata drifts out of sync."""

from __future__ import annotations

import re
from importlib.metadata import version as distribution_version
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "egypttranslit"
REPOSITORY = "https://github.com/edujbarrios/egypttranslit"


def _read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        raise SystemExit(f"missing required release file: {path}")
    text = target.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"required release file is empty: {path}")
    return text


def _extract(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        raise SystemExit(f"could not find {label}")
    return match.group(1)


def main() -> None:
    pyproject = _read("pyproject.toml")
    citation = _read("CITATION.cff")
    readme = _read("README.md")
    _read("LICENSE")
    _read("NOTICE")

    project_version = _extract(
        r'^version\s*=\s*"([^"]+)"\s*$', pyproject, "project version"
    )
    citation_version = _extract(
        r'^version:\s*"([^"]+)"\s*$', citation, "CITATION.cff version"
    )
    installed_version = distribution_version(PACKAGE)

    versions = {
        "pyproject.toml": project_version,
        "CITATION.cff": citation_version,
        "installed package": installed_version,
    }
    if len(set(versions.values())) != 1:
        details = ", ".join(f"{name}={value}" for name, value in versions.items())
        raise SystemExit(f"release versions are not synchronized: {details}")

    if 'license = "Apache-2.0"' not in pyproject:
        raise SystemExit("pyproject.toml must declare Apache-2.0")
    if f'Repository = "{REPOSITORY}"' not in pyproject:
        raise SystemExit("pyproject.toml repository URL is unexpected")
    if f'repository-code: "{REPOSITORY}"' not in citation:
        raise SystemExit("CITATION.cff repository URL is unexpected")
    if "CITATION.cff" not in readme:
        raise SystemExit("README.md must direct users to CITATION.cff")
    if "@software{" in readme or "@misc{" in readme:
        raise SystemExit("README.md duplicates BibTeX; keep citation metadata in CITATION.cff")

    print(f"release metadata OK: {PACKAGE} {project_version}")


if __name__ == "__main__":
    main()
