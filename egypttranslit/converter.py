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

# Auto parsing deliberately accepts only unusually strong ASCII evidence.
# Lowercase ``a`` and ``x`` are too common in ordinary Latin text, while a
# leading MdC capital can also be an ordinary title-case word (Data, Train,
# Hat, etc.). An uppercase shortcut inside a token, or an embedded ``3``, is
# distinctive enough to convert that token without inferring anything about
# neighbouring tokens. Callers who know the source is MdC should use
# :func:`parse_mdc` and avoid detection entirely.
_AUTO_MDC_MARKERS = frozenset("AHXSTD")

_TOKEN_RE = re.compile(
    re.escape(_UPPERCASE_XH)
    + r"|[A-Za-z0-9ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ]+"
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


def _has_explicit_mdc_signal(token: str) -> bool:
    """Return whether one ASCII token is distinctive enough for auto parsing."""
    if len(token) < 2:
        return False
    if "3" in token:
        return True
    return any(character in _AUTO_MDC_MARKERS for character in token[1:])


def _canonicalize_mdc_token(token: str) -> str:
    if token == _UPPERCASE_XH:
        return token
    return token.translate(_UNICODE_CANONICAL_TRANSLATION).translate(_MDC_TRANSLATION)


def parse(text: str) -> str:
    """Conservatively convert only self-signalling MdC tokens to Unicode.

    Automatic parsing never infers that neighbouring ASCII tokens are MdC.
    Ambiguous lowercase text, title-case words, one-letter shortcuts and words
    containing a plain ``x`` are preserved. Verified historical Unicode forms
    are still canonicalized. Use :func:`parse_mdc` when the input format is
    known and complete MdC conversion is desired.
    """
    prepared = _prepare_text(text)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if _has_explicit_mdc_signal(token):
            return _canonicalize_mdc_token(token)
        return token.translate(_UNICODE_CANONICAL_TRANSLATION)

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def parse_mdc(text: str) -> str:
    """Parse text that is explicitly known to use Manuel de Codage shortcuts.

    Unlike :func:`parse`, this function does not try to distinguish MdC from
    ordinary Latin prose. Unknown characters and punctuation are preserved.
    Editorial alternatives such as ``j``/``ỉ`` and ``q``/``ḳ`` are not guessed.
    """
    prepared = _prepare_text(text)

    def replace(match: re.Match[str]) -> str:
        return _canonicalize_mdc_token(match.group(0))

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def convert(text: str) -> str:
    """Alias for :func:`parse`."""
    return parse(text)
