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
_UNICODE_TRANSLITERATION = frozenset(
    "ꜢꜣꜤꜥȜȝʿḤḥḪḫẖŠšṮṯḎḏỈỉḲḳꞼꞽ"
)
_ALLOWED_TOKEN = _MDC_ASCII | _UNICODE_TRANSLITERATION

# Markers strong enough to identify an individual token as transliteration.
_STRONG_MARKERS = frozenset("AHxXSTD") | _UNICODE_TRANSLITERATION

# Document-wide inference deliberately excludes canonical Ꜣ/ꜣ, Ꜥ/ꜥ and
# Ꞽ/ꞽ. Those characters can be produced while converting otherwise ambiguous
# tokens; allowing them to become document-level evidence on the next call
# would make parsing non-idempotent and could corrupt neighbouring prose.
_DOCUMENT_MARKERS = frozenset("AHxXSTDȜȝʿỈỉḤḥḪḫŠšṮṯḎḏḲḳ")

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
    """Normalize known Egyptological Unicode variants without parsing MdC.

    This is the safest operation for already-Unicode or mixed scholarly text:
    it repairs only verified encoding equivalents and never interprets ASCII
    letters such as ``A`` or ``a`` as Manuel de Codage shortcuts.
    """
    prepared = _prepare_text(text)
    return unicodedata.normalize("NFC", prepared.translate(_UNICODE_CANONICAL_TRANSLATION))


def _is_mdc_token(token: str) -> bool:
    if token == _UPPERCASE_XH:
        return True
    return bool(token) and all(character in _ALLOWED_TOKEN for character in token)


def _lexical_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for token in _TOKEN_RE.findall(text):
        if token.isdigit() and token != "3":
            continue
        tokens.append(token)
    return tokens


def _document_looks_like_mdc(text: str) -> bool:
    """Conservatively decide whether a complete fragment looks like MdC."""
    tokens = _lexical_tokens(text)
    if not tokens or not all(_is_mdc_token(token) for token in tokens):
        return False

    if any(
        token == _UPPERCASE_XH
        or any(character in _DOCUMENT_MARKERS for character in token)
        for token in tokens
    ):
        return True

    if len(tokens) == 1:
        token = tokens[0]
        return len(token) <= 3 and "a" in token

    return False


def _should_convert_token(token: str, document_is_mdc: bool) -> bool:
    if token == _UPPERCASE_XH:
        return False
    if not _is_mdc_token(token):
        return False
    if document_is_mdc:
        return True
    if any(character in _STRONG_MARKERS for character in token):
        return True
    return "3" in token and len(token) > 1


def _canonicalize_token(token: str) -> str:
    if token == _UPPERCASE_XH:
        return token
    return token.translate(_UNICODE_CANONICAL_TRANSLATION).translate(_MDC_TRANSLATION)


def parse(text: str) -> str:
    """Conservatively parse likely MdC and return canonical Unicode.

    Ambiguous ordinary Latin text is preserved. Use :func:`parse_mdc` when the
    caller already knows that the input is Manuel de Codage transliteration.
    """
    prepared = _prepare_text(text)
    document_is_mdc = _document_looks_like_mdc(prepared)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if not _should_convert_token(token, document_is_mdc):
            return token.translate(_UNICODE_CANONICAL_TRANSLATION)
        return _canonicalize_token(token)

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def parse_mdc(text: str) -> str:
    """Parse text that is explicitly known to use Manuel de Codage shortcuts.

    Unlike :func:`parse`, this function does not try to distinguish MdC from
    ordinary Latin prose. Unknown characters and punctuation are preserved.
    Editorial alternatives such as ``j``/``ỉ`` and ``q``/``ḳ`` are not guessed.
    """
    prepared = _prepare_text(text)

    def replace(match: re.Match[str]) -> str:
        return _canonicalize_token(match.group(0))

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, prepared))


def convert(text: str) -> str:
    """Alias for :func:`parse`."""
    return parse(text)
