"""Fail fast when release metadata or publishing safety drifts out of sync."""

import importlib.metadata
import re
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


def _valid_orcid(identifier: str) -> bool:
    compact = identifier.replace("-", "")
    if re.fullmatch(r"\d{15}[\dX]", compact) is None:
        return False

    total = 0
    for character in compact[:-1]:
        total = (total + int(character)) * 2
    checksum = (12 - (total % 11)) % 11
    expected = "X" if checksum == 10 else str(checksum)
    return compact[-1] == expected


def _validate_release_workflow(workflow: str) -> None:
    if '      - "v*"' not in workflow:
        raise SystemExit("release workflow must retain version-tag publishing")
    if "workflow_dispatch:" not in workflow or "version:" not in workflow:
        raise SystemExit(
            "release workflow must expose an explicit manual version input"
        )
    if 'test "$GITHUB_REF" = "refs/heads/main"' not in workflow:
        raise SystemExit("manual PyPI releases must be restricted to main")
    if 'test "$REQUESTED_VERSION" = "$VERSION"' not in workflow:
        raise SystemExit("manual releases must match the prepared project version")
    if (
        "group: pypi-release" not in workflow
        or "cancel-in-progress: false" not in workflow
    ):
        raise SystemExit("release workflow must serialize production releases")
    if "name: pypi" not in workflow:
        raise SystemExit("release workflow must use the protected pypi environment")
    if workflow.count("id-token: write") != 1:
        raise SystemExit(
            "OIDC write permission must appear exactly once in release workflow"
        )
    if "username:" in workflow or "password:" in workflow or "PYPI_TOKEN" in workflow:
        raise SystemExit(
            "release workflow must use Trusted Publishing without static tokens"
        )
    if "if-no-files-found: error" not in workflow:
        raise SystemExit(
            "release artifact upload must fail when distributions are missing"
        )
    if (
        "Create GitHub release and tag" not in workflow
        or "contents: write" not in workflow
    ):
        raise SystemExit("successful PyPI publication must create a GitHub release/tag")

    action_refs = re.findall(r"^\s*uses:\s*[^@\s]+@([^\s#]+)", workflow, re.MULTILINE)
    if not action_refs:
        raise SystemExit("release workflow contains no pinned actions")
    unpinned = [
        ref for ref in action_refs if re.fullmatch(r"[0-9a-f]{40}", ref) is None
    ]
    if unpinned:
        raise SystemExit(f"release workflow contains unpinned action refs: {unpinned}")


def main() -> None:
    pyproject = _read("pyproject.toml")
    citation = _read("CITATION.cff")
    changelog = _read("CHANGELOG.md")
    readme = _read("README.md")
    release_workflow = _read(".github/workflows/release.yml")
    _read("LICENSE")
    _read("NOTICE")

    project_version = _extract(
        r'^version\s*=\s*"([^"]+)"\s*$', pyproject, "project version"
    )
    citation_version = _extract(
        r'^version:\s*"([^"]+)"\s*$', citation, "CITATION.cff version"
    )
    installed_version = importlib.metadata.version(PACKAGE)

    versions = {
        "pyproject.toml": project_version,
        "CITATION.cff": citation_version,
        "installed package": installed_version,
    }
    if len(set(versions.values())) != 1:
        details = ", ".join(f"{name}={value}" for name, value in versions.items())
        raise SystemExit(f"release versions are not synchronized: {details}")

    build_requirement = _extract(
        r'^requires\s*=\s*\["(setuptools==[^"]+)"\]\s*$',
        pyproject,
        "exact setuptools build requirement",
    )
    if build_requirement.count("==") != 1:
        raise SystemExit("setuptools build backend must be pinned exactly")

    citation_license = _extract(
        r'^license:\s*"([^"]+)"\s*$', citation, "CITATION.cff license"
    )
    orcid = _extract(
        r'^\s*orcid:\s*"https://orcid\.org/([0-9X-]+)"\s*$',
        citation,
        "CITATION.cff ORCID",
    )
    if not _valid_orcid(orcid):
        raise SystemExit(f"CITATION.cff contains an invalid ORCID checksum: {orcid}")

    if 'license = "Apache-2.0"' not in pyproject or citation_license != "Apache-2.0":
        raise SystemExit("release metadata must consistently declare Apache-2.0")
    if f'Repository = "{REPOSITORY}"' not in pyproject:
        raise SystemExit("pyproject.toml repository URL is unexpected")
    if f'repository-code: "{REPOSITORY}"' not in citation:
        raise SystemExit("CITATION.cff repository URL is unexpected")
    if 'title: "egypttranslit"' not in citation or "type: software" not in citation:
        raise SystemExit("CITATION.cff must identify egypttranslit as software")
    if f"## {project_version}" not in changelog:
        raise SystemExit(f"CHANGELOG.md has no entry for {project_version}")
    if 'egypttranslit = "egypttranslit.__main__:main"' not in pyproject:
        raise SystemExit("pyproject.toml console entry point is missing or unexpected")
    if "CITATION.cff" not in readme:
        raise SystemExit("README.md must direct users to CITATION.cff")
    if "@software{" in readme or "@misc{" in readme:
        raise SystemExit(
            "README.md duplicates BibTeX; keep citation metadata in CITATION.cff"
        )

    _validate_release_workflow(release_workflow)

    print(
        f"release metadata OK: {PACKAGE} {project_version}; "
        f"build backend {build_requirement}; ORCID checksum and workflow safety OK"
    )


if __name__ == "__main__":
    main()
