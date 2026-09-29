"""Conservative Egyptological transliteration to Unicode conversion."""

from __future__ import annotations

import re
import unicodedata

from .profiles import TransliterationProfile, apply_profile

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

# Unicode documents before Unicode 12 may encode Egyptological yod as i/I plus
# one of these combining marks. U+A7BD/U+A7BC are the preferred modern forms.
# Work at the full combining-cluster level because canonical ordering may place
# other scholarly/editorial marks between the base letter and the yod mark.
_LEGACY_YOD_MARKS = frozenset(("\u0313", "\u0357", "\u0486"))

# U+1E96 LATIN SMALL LETTER H WITH LINE BELOW has no single-code-point
# uppercase mapping. Unicode uppercases it to H + COMBINING MACRON BELOW.
# Keep that sequence atomic so the ASCII H is never mistaken for the MdC H
# shortcut when the caller supplies valid uppercase scholarly Unicode.
_UPPERCASE_XH = "H\u0331"

# Plain j and q are accepted but intentionally not rewritten by default.
# Callers that explicitly need a legacy fully-diacritic representation may
# request it through parse_mdc_profiled().
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


def _canonicalize_legacy_yod(text: str) -> str:
    """Replace one historical yod mark per i/I combining cluster."""
    decomposed = unicodedata.normalize("NFD", text)
    result: list[str] = []
    index = 0

    while index < len(decomposed):
        base = decomposed[index]
        if base not in {"i", "I"}:
            result.append(base)
            index += 1
            continue

        end = index + 1
        while end < len(decomposed) and unicodedata.combining(decomposed[end]):
            end += 1

        marks = decomposed[index + 1 : end]
        yod_positions = [
            position for position, mark in enumerate(marks) if mark in _LEGACY_YOD_MARKS
        ]
        if len(yod_positions) == 1:
            result.append("ꞽ" if base == "i" else "Ꞽ")
            yod_position = yod_positions[0]
            result.extend(
                mark for position, mark in enumerate(marks) if position != yod_position
            )
        else:
            result.append(base)
            result.extend(marks)

        index = end

    return "".join(result)


def _prepare_text(text: str) -> str:
    _require_text(text)
    return unicodedata.normalize("NFC", _canonicalize_legacy_yod(text))


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


def _is_numeric_run(token: str) -> bool:
    """Return whether *token* is an unambiguous multi-digit ASCII number."""
    return len(token) > 1 and token.isascii() and token.isdigit()


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


def _canonicalize_mdc_token(
    token: str, *, profile: TransliterationProfile = "default"
) -> str:
    if token == _UPPERCASE_XH or _is_sign_code(token) or _is_numeric_run(token):
        return token
    canonical = token.translate(_UNICODE_CANONICAL_TRANSLATION).translate(_MDC_TRANSLATION)
    return apply_profile(canonical, profile)


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


def _parse_mdc_with_profile(text: str, profile: TransliterationProfile) -> str:
    prepared = _prepare_text(text)
    # Validate the profile even for empty/punctuation-only input.
    apply_profile("", profile)

    def replace(match: re.Match[str]) -> str:
        return _canonicalize_mdc_token(match.group(0), profile=profile)

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def parse_mdc(text: str) -> str:
    """Convert known MdC shortcuts while preserving structure and API stability.

    This explicit mode assumes that the caller intentionally supplied MdC
    transliteration. Known shortcuts are converted even when unknown
    characters occur nearby. Multi-digit numbers, Gardiner/JSesh sign codes,
    unknown characters, punctuation and layout are preserved. Editorial
    alternatives such as ``j`` and ``q`` remain unchanged.
    """
    return _parse_mdc_with_profile(text, "default")


def parse_mdc_profiled(
    text: str, *, profile: TransliterationProfile = "default"
) -> str:
    """Convert known MdC shortcuts using an explicit editorial output profile.

    ``profile="legacy-diacritics"`` additionally renders ``j`` as
    Egyptological yod ``ꞽ`` and ``q`` as ``ḳ``. This advanced API is separate
    from :func:`parse_mdc` so the stable package-level converter contract stays
    one string in, one string out.
    """
    return _parse_mdc_with_profile(text, profile)


def convert(text: str) -> str:
    """Alias for :func:`parse`."""
    return parse(text)
