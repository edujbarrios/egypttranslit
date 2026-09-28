"""Conservative Egyptological transliteration to Unicode conversion."""

from __future__ import annotations

import re
import unicodedata

# Manuel de Codage ASCII shortcuts that have a clear Unicode equivalent.
_MDC_TRANSLATION = str.maketrans(
    {
        "A": "ꜣ",
        "a": "ꜥ",
        "H": "ḥ",
        "x": "ḫ",
        "X": "ẖ",
        "S": "š",
        "T": "ṯ",
        "D": "ḏ",
        "3": "ꜣ",
    }
)

# Historical Unicode representations that can be canonicalized without
# guessing an editorial convention. Case is preserved where Unicode provides
# a case pair.
_UNICODE_CANONICAL_TRANSLATION = str.maketrans(
    {
        "ȝ": "ꜣ",
        "Ȝ": "Ꜣ",
        "ʿ": "ꜥ",
        "ỉ": "ꞽ",
        "Ỉ": "Ꞽ",
    }
)

# Unicode documents before Unicode 12 may encode Egyptological yod as i plus
# one of these combining marks. U+A7BD/U+A7BC are the preferred modern forms.
_LEGACY_YOD_SEQUENCES = {
    "i\u0313": "ꞽ",
    "i\u0357": "ꞽ",
    "i\u0486": "ꞽ",
    "I\u0313": "Ꞽ",
    "I\u0357": "Ꞽ",
    "I\u0486": "Ꞽ",
}

# U+1E96 LATIN SMALL LETTER H WITH LINE BELOW has no single-code-point
# uppercase mapping. Unicode uppercases it to H + COMBINING MACRON BELOW.
# Keep that sequence atomic so the ASCII H is never mistaken for the MdC H
# shortcut when the caller supplies valid uppercase scholarly Unicode.
_UPPERCASE_XH = "H\u0331"

# Plain j and q are accepted but intentionally not rewritten. IFAO documents
# j/ỉ and q/ḳ as legitimate editorial alternatives, not encoding errors.
_MDC_ASCII = frozenset("AaiyjwybpfmnrhHxXzsSqkgtTdD3")
_UNICODE_TRANSLITERATION = frozenset("ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ")
_ALLOWED_TOKEN = _MDC_ASCII | _UNICODE_TRANSLITERATION

# Gardiner/Hieroglyphica and JSesh sign identifiers are part of MdC-family
# data, but they are not transliteration. Protect only strings accepted by the
# normative source grammars in Unicode UAX #57:
#   kEH_HG:    ([A-IK-Z]|AA)\d{1,3}[A-Za-z]{0,2}
#   kEH_JSesh: ([A-IK-Z]|Aa|NL|NU|Ff)\d{1,3}[A-Za-z]{0,5}
#           or (US1|US22|US248|US685)([A-IK-Z]|Aa|NL|NU)
#              \d{1,3}[A-Za-z]{0,5}
# https://unicode.org/reports/tr57/
_SIGN_CODE_RE = re.compile(
    r"(?:"
    r"(?:[A-IK-Z]|AA)\d{1,3}[A-Za-z]{0,2}"
    r"|(?:[A-IK-Z]|Aa|NL|NU|Ff)\d{1,3}[A-Za-z]{0,5}"
    r"|(?:US1|US22|US248|US685)(?:[A-IK-Z]|Aa|NL|NU)"
    r"\d{1,3}[A-Za-z]{0,5}"
    r")\Z"
)

# Auto parsing deliberately accepts only unusually strong *and singular*
# ASCII evidence. Lowercase ``a`` and ``x`` are too common in ordinary Latin
# text, while a leading MdC capital can also be an ordinary title-case word.
# Exactly one embedded ``3`` or internal MdC uppercase shortcut is enough to
# convert a token such as ``n3``, ``nTr`` or ``mAat``. Leading strong markers
# are counted when deciding ambiguity but never suffice by themselves. Thus
# acronym-like or multiply marked tokens are preserved. Callers who know the
# source is MdC should use :func:`parse_mdc` and avoid detection entirely.
_AUTO_MDC_MARKERS = frozenset("AHXSTD")

_TOKEN_RE = re.compile(
    re.escape(_UPPERCASE_XH) + r"|[A-Za-z0-9ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ]+"
)


def _require_text(text: str) -> None:
    if not isinstance(text, str):
        raise TypeError("text must be a string")


def _prepare_text(text: str) -> str:
    _require_text(text)
    for sequence, replacement in _LEGACY_YOD_SEQUENCES.items():
        text = text.replace(sequence, replacement)
    return unicodedata.normalize("NFC", text)


def normalize_unicode(text: str) -> str:
    """Normalize verified Egyptological Unicode variants without parsing MdC.

    This is the safest operation for already-Unicode or mixed scholarly text:
    it repairs only verified encoding equivalents and never interprets ASCII
    letters such as ``A`` or ``a`` as Manuel de Codage shortcuts.
    """
    prepared = _prepare_text(text)
    return unicodedata.normalize(
        "NFC", prepared.translate(_UNICODE_CANONICAL_TRANSLATION)
    )


def _is_sign_code(token: str) -> bool:
    """Return whether *token* is a protected Gardiner/JSesh sign identifier."""
    return _SIGN_CODE_RE.fullmatch(token) is not None


def _is_mdc_token(token: str) -> bool:
    if token == _UPPERCASE_XH:
        return True
    return bool(token) and all(character in _ALLOWED_TOKEN for character in token)


def _is_auto_marker(character: str) -> bool:
    return character == "3" or character in _AUTO_MDC_MARKERS


def _auto_mdc_signal_count(token: str) -> int:
    """Count distinctive ASCII signals used by conservative auto parsing."""
    return sum(_is_auto_marker(character) for character in token)


def _has_explicit_mdc_signal(token: str) -> bool:
    """Return whether one ASCII token is distinctive enough for auto parsing."""
    if _is_sign_code(token):
        return False
    if len(token) < 2 or not _is_mdc_token(token):
        return False
    return _auto_mdc_signal_count(token) == 1 and any(
        _is_auto_marker(character) for character in token[1:]
    )


def _canonicalize_mdc_token(token: str) -> str:
    if token == _UPPERCASE_XH or _is_sign_code(token):
        return token
    return token.translate(_UNICODE_CANONICAL_TRANSLATION).translate(_MDC_TRANSLATION)


def parse(text: str) -> str:
    """Conservatively convert only self-signalling MdC tokens to Unicode.

    Automatic parsing never infers that neighbouring ASCII tokens are MdC.
    Ambiguous lowercase text, title-case words, one-letter shortcuts, tokens
    with multiple strong MdC markers, Gardiner/JSesh sign codes, and words
    containing only a plain ``x`` are preserved. Verified historical Unicode
    forms are still canonicalized. Use :func:`parse_mdc` when the input format
    is known and complete MdC transliteration conversion is desired.
    """
    prepared = _prepare_text(text)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if _has_explicit_mdc_signal(token):
            return _canonicalize_mdc_token(token)
        return token.translate(_UNICODE_CANONICAL_TRANSLATION)

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def parse_mdc(text: str) -> str:
    """Convert known MdC transliteration shortcuts while preserving structure.

    This explicit mode assumes that the caller intentionally supplied MdC
    transliteration. Known shortcuts are converted even when unknown
    characters occur nearby. Gardiner/JSesh sign codes, unknown characters,
    punctuation and layout are preserved. Editorial alternatives such as
    ``j``/``ỉ`` and ``q``/``ḳ`` are not guessed.
    """
    prepared = _prepare_text(text)

    def replace(match: re.Match[str]) -> str:
        return _canonicalize_mdc_token(match.group(0))

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def convert(text: str) -> str:
    """Alias for :func:`parse`."""
    return parse(text)
