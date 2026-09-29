"""Diagnostics for transliteration conversion.

The conversion API intentionally preserves ambiguous data.  This module adds
an opt-in inspection layer for applications that want to reject suspicious
mixed-encoding tokens before accepting converted output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from .converter import normalize_unicode, parse, parse_mdc
from .profiles import TransliterationProfile

ConversionMode = Literal["auto", "mdc", "unicode"]

_ASCII_TRANSLITERATION = frozenset("AaiyjwybpfmnrhHxXzsSqkgtTdD3")
_UNICODE_TRANSLITERATION = frozenset("ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ")
_TOKEN_RE = re.compile(r"[A-Za-z0-9ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ]+")
_SIGN_CODE_RE = re.compile(
    r"(?:"
    r"(?:[A-IK-Z]|AA)\d{1,3}[A-Za-z]{0,2}"
    r"|(?:[A-IK-Z]|Aa|NL|NU|Ff)\d{1,3}[A-Za-z]{0,5}"
    r"|(?:US1|US22|US248|US685)(?:[A-IK-Z]|Aa|NL|NU)"
    r"\d{1,3}[A-Za-z]{0,5}"
    r")\Z"
)


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Converted text plus machine-readable diagnostic information."""

    source: str
    text: str
    mode: ConversionMode
    changed: bool
    warnings: tuple[str, ...]


def _mixed_encoding_warnings(text: str) -> tuple[str, ...]:
    warnings: list[str] = []
    for match in _TOKEN_RE.finditer(text):
        token = match.group(0)
        if _SIGN_CODE_RE.fullmatch(token):
            continue
        has_ascii = any(character in _ASCII_TRANSLITERATION for character in token)
        has_unicode = any(character in _UNICODE_TRANSLITERATION for character in token)
        if has_ascii and has_unicode:
            warnings.append(
                f"mixed ASCII/Unicode transliteration token {token!r} "
                f"at offset {match.start()}"
            )
    return tuple(warnings)


def analyze(
    text: str,
    *,
    mode: ConversionMode = "auto",
    profile: TransliterationProfile = "default",
) -> ConversionResult:
    """Convert *text* and return diagnostics without rejecting suspicious data."""
    if mode == "auto":
        converted = parse(text)
    elif mode == "mdc":
        converted = parse_mdc(text, profile=profile)
    elif mode == "unicode":
        converted = normalize_unicode(text)
    else:
        raise ValueError(f"unknown conversion mode {mode!r}")

    warnings = _mixed_encoding_warnings(text)
    return ConversionResult(
        source=text,
        text=converted,
        mode=mode,
        changed=converted != text,
        warnings=warnings,
    )


def validate(
    text: str,
    *,
    mode: ConversionMode = "mdc",
    profile: TransliterationProfile = "default",
) -> ConversionResult:
    """Return diagnostics or raise ``ValueError`` for suspicious mixed tokens."""
    result = analyze(text, mode=mode, profile=profile)
    if result.warnings:
        raise ValueError("; ".join(result.warnings))
    return result
