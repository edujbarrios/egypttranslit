"""Diagnostics for transliteration conversion.

The conversion API intentionally preserves ambiguous data. This module adds an
opt-in inspection layer for applications that want machine-readable evidence
about the input before accepting converted output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from .converter import normalize_unicode, parse, parse_mdc_profiled
from .profiles import TransliterationProfile

ConversionMode = Literal["auto", "mdc", "unicode"]
DetectedInput = Literal["mdc", "unicode", "mixed", "ambiguous", "none"]

_ASCII_TRANSLITERATION = frozenset("AaiyjwybpfmnrhHxXzsSqkgtTdD3")
_UNICODE_TRANSLITERATION = frozenset("ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ")
_STRONG_MDC_MARKERS = frozenset("AHXSTD3")
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
    """Converted text plus machine-readable diagnostic information.

    ``confidence`` is a deterministic heuristic score describing how strongly
    the characters support ``detected``. It is not a statistical probability.
    """

    source: str
    text: str
    mode: ConversionMode
    changed: bool
    detected: DetectedInput
    confidence: float
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


def _detect_input(text: str, warnings: tuple[str, ...]) -> tuple[DetectedInput, float]:
    if warnings:
        return "mixed", 1.0

    tokens = [
        match.group(0)
        for match in _TOKEN_RE.finditer(text)
        if not _SIGN_CODE_RE.fullmatch(match.group(0))
    ]
    if not tokens:
        return "none", 1.0

    has_unicode = any(
        character in _UNICODE_TRANSLITERATION
        for token in tokens
        for character in token
    )
    has_ascii = any(
        character in _ASCII_TRANSLITERATION
        for token in tokens
        for character in token
    )
    has_strong_mdc = any(
        character in _STRONG_MDC_MARKERS
        for token in tokens
        for character in token[1:]
    )

    if has_unicode:
        return "unicode", 1.0
    if has_strong_mdc:
        return "mdc", 0.9
    if has_ascii:
        return "ambiguous", 0.0
    return "none", 1.0


def analyze(
    text: str,
    *,
    mode: ConversionMode = "auto",
    profile: TransliterationProfile = "default",
) -> ConversionResult:
    """Convert *text* and return deterministic, non-probabilistic diagnostics."""
    if mode == "auto":
        converted = parse(text)
    elif mode == "mdc":
        converted = parse_mdc_profiled(text, profile=profile)
    elif mode == "unicode":
        converted = normalize_unicode(text)
    else:
        raise ValueError(f"unknown conversion mode {mode!r}")

    warnings = _mixed_encoding_warnings(text)
    detected, confidence = _detect_input(text, warnings)
    return ConversionResult(
        source=text,
        text=converted,
        mode=mode,
        changed=converted != text,
        detected=detected,
        confidence=confidence,
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
