"""Egyptological transliteration to canonical Unicode."""

import importlib.metadata

from .converter import convert, normalize_unicode, parse, parse_mdc

__all__ = ["convert", "normalize_unicode", "parse", "parse_mdc"]

try:
    __version__ = importlib.metadata.version("egypttranslit")
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0+unknown"
