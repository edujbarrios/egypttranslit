"""Egyptological transliteration to canonical Unicode."""

from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _distribution_version

from .converter import convert, normalize_unicode, parse, parse_mdc
from .diagnostics import ConversionResult, analyze, validate

__all__ = [
    "ConversionResult",
    "analyze",
    "convert",
    "normalize_unicode",
    "parse",
    "parse_mdc",
    "validate",
]

try:
    __version__ = _distribution_version("egypttranslit")
except _PackageNotFoundError:  # pragma: no cover
    __version__ = "0+unknown"
