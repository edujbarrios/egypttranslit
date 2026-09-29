"""Prepare synchronized release metadata for a new final version."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def parse_version(value: str) -> tuple[int, int, int]:
    """Parse a strict three-component final release version."""
    match = _VERSION_RE.fullmatch(value)
    if match is None:
        raise ValueError("version must use X.Y.Z numeric release syntax")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def update_pyproject(text: str, version: str) -> str:
    """Replace the project version exactly once while preserving line endings."""
    updated, count = re.subn(
        r'(?m)^version[ \t]*=[ \t]*"[^"]+"[ \t]*$',
        f'version = "{version}"',
        text,
        count=1,
    )
    if count != 1:
        raise ValueError("could not replace exactly one pyproject version")
    return updated


def update_citation(text: str, version: str) -> str:
    """Replace the citation version exactly once while preserving line endings."""
    updated, count = re.subn(
        r'(?m)^version:[ \t]*"[^"]+"[ \t]*$',
        f'version: "{version}"',
        text,
        count=1,
    )
    if count != 1:
        raise ValueError("could not replace exactly one CITATION.cff version")
    return updated


def update_changelog(text: str, version: str, notes: str) -> str:
    """Insert one new changelog section before the current latest release."""
    heading = f"## {version}"
    if heading in text:
        raise ValueError(f"CHANGELOG.md already contains {heading}")

    normalized_notes = notes.strip()
    if not normalized_notes:
        raise ValueError("release notes must not be empty")

    match = re.search(r"(?m)^## \S.*$", text)
    if match is None:
        raise ValueError("CHANGELOG.md contains no release section")

    section = f"{heading}\n\n{normalized_notes}\n\n"
    return text[: match.start()] + section + text[match.start() :]


def prepare_release(root: Path, version: str, notes: str) -> None:
    """Update all synchronized release metadata files in place."""
    target = parse_version(version)

    pyproject_path = root / "pyproject.toml"
    citation_path = root / "CITATION.cff"
    changelog_path = root / "CHANGELOG.md"

    pyproject = pyproject_path.read_text(encoding="utf-8")
    citation = citation_path.read_text(encoding="utf-8")
    changelog = changelog_path.read_text(encoding="utf-8")

    current_match = re.search(
        r'(?m)^version[ \t]*=[ \t]*"([^"]+)"[ \t]*$',
        pyproject,
    )
    if current_match is None:
        raise ValueError("could not find current project version")
    current = parse_version(current_match.group(1))
    if target <= current:
        raise ValueError(
            f"new version {version} must be greater than current version "
            f"{current_match.group(1)}"
        )

    pyproject_path.write_text(update_pyproject(pyproject, version), encoding="utf-8")
    citation_path.write_text(update_citation(citation, version), encoding="utf-8")
    changelog_path.write_text(
        update_changelog(changelog, version, notes),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()

    try:
        prepare_release(ROOT, args.version, args.notes)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"prepared release metadata for {args.version}")


if __name__ == "__main__":
    main()
