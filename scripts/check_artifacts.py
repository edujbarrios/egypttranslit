"""Validate wheel and sdist contents before any release is considered publishable."""

from __future__ import annotations

import re
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path, PurePosixPath

DIST = Path("dist")
PACKAGE = "egypttranslit"

_REQUIRED_WHEEL_FILES = {
    "egypttranslit/__init__.py",
    "egypttranslit/__main__.py",
    "egypttranslit/converter.py",
    "egypttranslit/py.typed",
}

_REQUIRED_SDIST_FILES = {
    "CHANGELOG.md",
    "CITATION.cff",
    "LICENSE",
    "MANIFEST.in",
    "NOTICE",
    "README.md",
    "RELEASING.md",
    "pyproject.toml",
    "egypttranslit/__init__.py",
    "egypttranslit/__main__.py",
    "egypttranslit/converter.py",
    "egypttranslit/py.typed",
    "scripts/check_artifacts.py",
    "scripts/check_release.py",
    "tests/test_cli.py",
    "tests/test_converter.py",
    "tests/test_parser_contracts.py",
    "tests/test_unicode_contract.py",
}

_EXPECTED_PROJECT_URLS = {
    "Homepage, https://edujbarrios.com",
    "Repository, https://github.com/edujbarrios/egypttranslit",
    "Issues, https://github.com/edujbarrios/egypttranslit/issues",
    "Citation, https://github.com/edujbarrios/egypttranslit/blob/main/CITATION.cff",
    "Changelog, https://github.com/edujbarrios/egypttranslit/blob/main/CHANGELOG.md",
}

_FORBIDDEN_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
_FORBIDDEN_NAMES = {".DS_Store", ".env", "Thumbs.db"}
_FORBIDDEN_SUFFIXES = {
    ".dll",
    ".dylib",
    ".exe",
    ".key",
    ".p12",
    ".pfx",
    ".pem",
    ".pyc",
    ".pyd",
    ".pyo",
    ".so",
}


def _fail(message: str) -> None:
    raise SystemExit(message)


def _single(pattern: str) -> Path:
    matches = sorted(DIST.glob(pattern))
    if len(matches) != 1:
        _fail(f"expected exactly one {pattern!r} artifact, found {len(matches)}")
    return matches[0]


def _project_version() -> str:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', pyproject, re.MULTILINE)
    if match is None:
        _fail("could not read project version from pyproject.toml")
    return match.group(1)


def _validate_member_name(name: str, *, archive: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        _fail(f"unsafe path in {archive}: {name}")
    if any(part in _FORBIDDEN_PARTS for part in path.parts):
        _fail(f"forbidden cache/VCS path in {archive}: {name}")
    if path.name in _FORBIDDEN_NAMES or path.suffix.lower() in _FORBIDDEN_SUFFIXES:
        _fail(f"forbidden file in {archive}: {name}")


def _audit_core_metadata(text: str, *, source: str, version: str) -> None:
    metadata = Parser().parsestr(text)
    expected_fields = {
        "Name": PACKAGE,
        "Version": version,
        "Requires-Python": ">=3.10",
        "License-Expression": "Apache-2.0",
        "Description-Content-Type": "text/markdown",
    }
    for field, expected in expected_fields.items():
        actual = metadata.get(field)
        if actual != expected:
            _fail(f"{source} {field} is {actual!r}; expected {expected!r}")

    if metadata.get_all("Requires-Dist"):
        _fail(f"{source} unexpectedly declares runtime dependencies")
    if metadata.get_all("Provides-Extra"):
        _fail(f"{source} unexpectedly declares optional dependency extras")

    license_files = {
        PurePosixPath(value).name for value in metadata.get_all("License-File", [])
    }
    if license_files != {"LICENSE", "NOTICE"}:
        _fail(f"{source} license files are unexpected: {sorted(license_files)}")

    project_urls = set(metadata.get_all("Project-URL", []))
    missing_urls = sorted(_EXPECTED_PROJECT_URLS - project_urls)
    if missing_urls:
        _fail(f"{source} is missing Project-URL metadata: {', '.join(missing_urls)}")


def _audit_wheel(path: Path, *, version: str) -> None:
    expected_name = f"{PACKAGE}-{version}-py3-none-any.whl"
    if path.name != expected_name:
        _fail(f"wheel must be universal {expected_name!r}; found {path.name!r}")

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()

    if len(names) != len(set(names)):
        _fail(f"duplicate archive member in wheel: {path.name}")
    for name in names:
        _validate_member_name(name, archive=path.name)

    members = set(names)
    missing = sorted(_REQUIRED_WHEEL_FILES - members)
    if missing:
        _fail(f"wheel is missing required files: {', '.join(missing)}")

    metadata_files = [name for name in names if name.endswith(".dist-info/METADATA")]
    if len(metadata_files) != 1:
        _fail("wheel must contain exactly one .dist-info/METADATA file")
    metadata_name = metadata_files[0]
    dist_info = metadata_name.removesuffix("METADATA")

    for required in ("WHEEL", "RECORD", "entry_points.txt"):
        if f"{dist_info}{required}" not in members:
            _fail(f"wheel is missing {dist_info}{required}")

    with zipfile.ZipFile(path) as archive:
        metadata_text = archive.read(metadata_name).decode("utf-8")
        wheel_text = archive.read(f"{dist_info}WHEEL").decode("utf-8")
        entry_points = archive.read(f"{dist_info}entry_points.txt").decode("utf-8")
    _audit_core_metadata(metadata_text, source="wheel METADATA", version=version)

    wheel_metadata = Parser().parsestr(wheel_text)
    if wheel_metadata.get("Root-Is-Purelib", "").lower() != "true":
        _fail("wheel must declare Root-Is-Purelib: true")
    tags = set(wheel_metadata.get_all("Tag", []))
    if tags != {"py3-none-any"}:
        _fail(f"wheel compatibility tags are unexpected: {sorted(tags)}")

    if "[console_scripts]" not in entry_points or not any(
        line.strip() == "egypttranslit = egypttranslit.__main__:main"
        for line in entry_points.splitlines()
    ):
        _fail("wheel console entry point is missing or unexpected")

    for license_name in ("LICENSE", "NOTICE"):
        if not any(
            name.startswith(dist_info)
            and "/licenses/" in name
            and name.endswith(f"/{license_name}")
            for name in names
        ):
            _fail(f"wheel is missing packaged {license_name}")

    allowed_roots = {"egypttranslit", dist_info.rstrip("/")}
    for name in names:
        root = PurePosixPath(name).parts[0]
        if root not in allowed_roots:
            _fail(f"unexpected top-level wheel content: {name}")
        if name.startswith(("tests/", "scripts/", ".github/")):
            _fail(f"development-only content leaked into wheel: {name}")


def _audit_sdist(path: Path, *, version: str) -> None:
    expected_prefix = f"{PACKAGE}-{version}"
    if path.name != f"{expected_prefix}.tar.gz":
        _fail(f"sdist filename does not match project version {version}: {path.name}")

    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()

    names = [member.name for member in members]
    if len(names) != len(set(names)):
        _fail(f"duplicate archive member in sdist: {path.name}")
    for name in names:
        _validate_member_name(name, archive=path.name)

    roots = {PurePosixPath(name).parts[0] for name in names if name}
    if roots != {expected_prefix}:
        _fail(f"sdist top-level directory is unexpected: {sorted(roots)}")
    root = expected_prefix

    relative_files: set[str] = set()
    for member in members:
        if member.issym() or member.islnk():
            _fail(f"links are not allowed in sdist: {member.name}")
        parts = PurePosixPath(member.name).parts
        if member.isfile() and len(parts) > 1:
            relative_files.add(PurePosixPath(*parts[1:]).as_posix())

    missing = sorted(_REQUIRED_SDIST_FILES - relative_files)
    if missing:
        _fail(f"sdist is missing required files: {', '.join(missing)}")

    if any(name.startswith((".github/", "dist/", "build/")) for name in relative_files):
        _fail("sdist contains repository/build-only files")

    pkg_info_name = f"{root}/PKG-INFO"
    if pkg_info_name not in names:
        _fail("sdist is missing PKG-INFO")
    with tarfile.open(path, mode="r:gz") as archive:
        pkg_info_file = archive.extractfile(pkg_info_name)
        if pkg_info_file is None:
            _fail("could not read PKG-INFO from sdist")
        pkg_info = pkg_info_file.read().decode("utf-8")
    _audit_core_metadata(pkg_info, source="sdist PKG-INFO", version=version)

    print(f"artifact audit OK: {path.name} ({root})")


def main() -> None:
    if not DIST.is_dir():
        _fail("dist directory does not exist; build artifacts first")

    version = _project_version()
    wheel = _single("*.whl")
    sdist = _single("*.tar.gz")
    _audit_wheel(wheel, version=version)
    _audit_sdist(sdist, version=version)
    print(f"artifact audit OK: {wheel.name}; metadata version {version}")


if __name__ == "__main__":
    main()
