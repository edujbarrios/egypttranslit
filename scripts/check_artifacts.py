"""Validate wheel and sdist contents before any release is considered publishable."""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path, PurePosixPath

DIST = Path("dist")

_REQUIRED_WHEEL_FILES = {
    "egypttranslit/__init__.py",
    "egypttranslit/converter.py",
    "egypttranslit/py.typed",
}

_REQUIRED_SDIST_FILES = {
    "CITATION.cff",
    "LICENSE",
    "MANIFEST.in",
    "NOTICE",
    "README.md",
    "RELEASING.md",
    "pyproject.toml",
    "egypttranslit/__init__.py",
    "egypttranslit/converter.py",
    "egypttranslit/py.typed",
    "scripts/check_artifacts.py",
    "scripts/check_release.py",
    "tests/test_converter.py",
    "tests/test_parser_contracts.py",
    "tests/test_unicode_contract.py",
}

_FORBIDDEN_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
_FORBIDDEN_NAMES = {".DS_Store", ".env", "Thumbs.db"}
_FORBIDDEN_SUFFIXES = {".key", ".p12", ".pfx", ".pem", ".pyc", ".pyo"}


def _fail(message: str) -> None:
    raise SystemExit(message)


def _single(pattern: str) -> Path:
    matches = sorted(DIST.glob(pattern))
    if len(matches) != 1:
        _fail(f"expected exactly one {pattern!r} artifact, found {len(matches)}")
    return matches[0]


def _validate_member_name(name: str, *, archive: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        _fail(f"unsafe path in {archive}: {name}")
    if any(part in _FORBIDDEN_PARTS for part in path.parts):
        _fail(f"forbidden cache/VCS path in {archive}: {name}")
    if path.name in _FORBIDDEN_NAMES or path.suffix.lower() in _FORBIDDEN_SUFFIXES:
        _fail(f"forbidden file in {archive}: {name}")


def _audit_wheel(path: Path) -> None:
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
    dist_info = metadata_files[0].removesuffix("METADATA")

    for required in ("WHEEL", "RECORD"):
        if f"{dist_info}{required}" not in members:
            _fail(f"wheel is missing {dist_info}{required}")
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


def _audit_sdist(path: Path) -> None:
    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()

    names = [member.name for member in members]
    if len(names) != len(set(names)):
        _fail(f"duplicate archive member in sdist: {path.name}")
    for name in names:
        _validate_member_name(name, archive=path.name)

    roots = {PurePosixPath(name).parts[0] for name in names if name}
    if len(roots) != 1:
        _fail(f"sdist must have one top-level directory, found: {sorted(roots)}")
    root = next(iter(roots))

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

    print(f"artifact audit OK: {path.name} ({root})")


def main() -> None:
    if not DIST.is_dir():
        _fail("dist directory does not exist; build artifacts first")

    wheel = _single("*.whl")
    sdist = _single("*.tar.gz")
    _audit_wheel(wheel)
    _audit_sdist(sdist)
    print(f"artifact audit OK: {wheel.name}")


if __name__ == "__main__":
    main()
