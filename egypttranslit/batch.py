"""Batch helpers for Egyptological transliteration conversion."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from .converter import normalize_unicode, parse, parse_mdc, parse_mdc_profiled
from .profiles import TransliterationProfile


def _convert_many(
    texts: Iterable[str], converter: Callable[[str], str]
) -> tuple[str, ...]:
    if isinstance(texts, (str, bytes)):
        raise TypeError("texts must be an iterable of strings, not a single string")
    return tuple(converter(text) for text in texts)


def parse_many(texts: Iterable[str]) -> tuple[str, ...]:
    """Conservatively parse multiple transliterations in input order."""
    return _convert_many(texts, parse)


def parse_mdc_many(texts: Iterable[str]) -> tuple[str, ...]:
    """Convert multiple known MdC transliterations in input order."""
    return _convert_many(texts, parse_mdc)


def parse_mdc_profiled_many(
    texts: Iterable[str], *, profile: TransliterationProfile = "default"
) -> tuple[str, ...]:
    """Convert multiple MdC transliterations using one editorial profile."""
    if isinstance(texts, (str, bytes)):
        raise TypeError("texts must be an iterable of strings, not a single string")
    return tuple(parse_mdc_profiled(text, profile=profile) for text in texts)


def normalize_unicode_many(texts: Iterable[str]) -> tuple[str, ...]:
    """Normalize multiple already-Unicode Egyptological strings in input order."""
    return _convert_many(texts, normalize_unicode)
