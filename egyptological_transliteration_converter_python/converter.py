"""Conservative Egyptological transliteration to Unicode conversion."""

from __future__ import annotations

import re
import unicodedata

# Core Manuel de Codage shortcuts plus two widely encountered textual variants:
# ``3`` for aleph and the IFAO-style Unicode signs ȝ / ʿ.
_TRANSLATION = str.maketrans(
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
        "ȝ": "ꜣ",
        "ʿ": "ꜥ",
    }
)

# ASCII characters used by MdC transliteration. Plain j is accepted as a
# textual yod variant but is intentionally not rewritten: choosing i/j/ỉ is an
# editorial convention, not a character-encoding repair.
_MDC_ASCII = frozenset("AaiyjwybpfmnrhHxXzsSqkgtTdD3")
_UNICODE_TRANSLITERATION = frozenset("ꜣꜥȝʿḥḫẖšṯḏỉḳ")
_ALLOWED_TOKEN = _MDC_ASCII | _UNICODE_TRANSLITERATION
_STRONG_MARKERS = frozenset("AHxXSTD") | _UNICODE_TRANSLITERATION
_TOKEN_RE = re.compile(r"[A-Za-z0-9ꜣꜥȝʿḥḫẖšṯḏỉḳ]+")


def _is_mdc_token(token: str) -> bool:
    return bool(token) and all(character in _ALLOWED_TOKEN for character in token)


def _document_looks_like_mdc(text: str) -> bool:
    """Return True when every lexical token is compatible with MdC.

    Numeric-only tokens are neutral so catalogue numbers, dates, line numbers,
    and similar research metadata do not disable conversion of an otherwise MdC
    string.
    """
    lexical_tokens: list[str] = []
    for token in _TOKEN_RE.findall(text):
        if token.isdigit() and token != "3":
            continue
        lexical_tokens.append(token)

    return bool(lexical_tokens) and all(_is_mdc_token(token) for token in lexical_tokens)


def _should_convert_token(token: str, document_is_mdc: bool) -> bool:
    if not _is_mdc_token(token):
        return False

    if document_is_mdc:
        return True

    # In mixed prose, only convert tokens that visibly signal Egyptological
    # transliteration. This keeps ordinary surrounding language unchanged.
    if any(character in _STRONG_MARKERS for character in token):
        return True

    # ``3`` is an accepted aleph variant, but a bare number 3 in prose is far
    # more likely to be a number. Convert it only when it occurs inside an MdC
    # token such as 3b or n3.
    return "3" in token and len(token) > 1


def parse(text: str) -> str:
    """Parse Egyptological transliteration and return normalized Unicode.

    The parser understands core MdC shortcuts, common aleph/ayin variants,
    decomposed Unicode, editorial punctuation, and mixed prose. Characters it
    cannot identify safely are preserved unchanged.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = unicodedata.normalize("NFC", text)
    document_is_mdc = _document_looks_like_mdc(normalized)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if not _should_convert_token(token, document_is_mdc):
            return token
        return token.translate(_TRANSLATION)

    return unicodedata.normalize("NFC", _TOKEN_RE.sub(replace, normalized))


def convert(text: str) -> str:
    """Alias for :func:`parse`."""
    return parse(text)
