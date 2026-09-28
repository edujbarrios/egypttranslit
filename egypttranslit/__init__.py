"""Egyptological transliteration to canonical Unicode."""

from importlib.metadata import PackageNotFoundError, version as _distribution_version

from .converter import convert, normalize_unicode, parse, parse_mdc

__all__ = ["parse", "parse_mdc", "normalize_unicode", "convert"]

try:
    __version__ = _distribution_version("egypttranslit")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0+unknown"
