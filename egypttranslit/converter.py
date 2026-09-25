"""Conservative Egyptological transliteration to Unicode conversion."""

from __future__ import annotations

import re
import unicodedata

# Core Manuel de Codage shortcuts plus textual/Unicode variants encountered in
# Egyptological material.
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
        # IFAO has historically used ỉ as one representation of the reed-leaf
        # sign. Unicode now provides the dedicated Egyptological yod ꞽ.
        "ỉ": "ꞽ",
    }
)

# Unicode documents before Unicode 12 may encode Egyptological yod as i plus
# one of these combining marks. U+A7BD is the dedicated modern character.
_LEGACY_YOD_SEQUENCES = {
    "i\u0313": "ꞽ",  # COMBINING COMMA ABOVE
    "i\u0357": "ꞽ",  # COMBINING RIGHT HALF RING ABOVE
    "i\u0486": "ꞽ",  # COMBINING CYRILLIC PSILI PNEUMATA
    "I\u0313": "Ꞽ",
    "I\u0357": "Ꞽ",
    "I\u0486": "Ꞽ",
}

# ASCII characters used by MdC transliteration. Plain j is accepted as a
# textual yod convention but is intentionally not rewritten: j versus ꞽ is an
# editorial/transliteration convention, not merely an encoding repair.
_MDC_ASCII = frozenset("AaiyjwybpfmnrhHxXzsSqkgtTdD3")
_UNICODE_TRANSLITERATION = frozenset("ꜣꜥȝʿḥḫẖšṯḏỉḳꞽꞼ")
_ALLOWED_TOKEN = _MDC_ASCII | _UNICODE_TRANSLITERATION
_STRONG_MARKERS = frozenset("AHxXSTD") | _UNICODE_TRANSLITERATION
_TOKEN_RE = re.compile(r"[A-Za-z0-9ꜣꜥȝʿḥḫẖšṯḏỉḳꞽꞼ]+")


def _canonicalize_legacy_yod(text: str) -> str:
    for sequence, replacement in _LEGACY_YOD_SEQUENCES.items():
        text = text.replace(sequence, replacement)
    return text


def _is_mdc_token(token: str) -> bool:
    return bool(token) and all(character in _ALLOWED_TOKEN for character in token)


def _lexical_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for token in _TOKEN_RE.findall(text):
        if token.isdigit() and token != "3":
            continue
        tokens.append(token)
    return tokens


def _document_looks_like_mdc(text: str) -> bool:
    """Conservatively decide whether a complete fragment looks like MdC.

    A whole fragment is treated as MdC only when every lexical token is
    compatible with MdC *and* there is enough evidence that the fragment is
    transliteration rather than ordinary Latin-script prose.
    """
    tokens = _lexical_tokens(text)
    if not tokens or not all(_is_mdc_token(token) for token in tokens):
        return False

    if len(tokens) > 1:
        return True

    token = tokens[0]
    if any(character in _STRONG_MARKERS for character in token):
        return True

    # Short forms such as ``ra`` occur commonly in MdC. Keeping this exception
    # narrow avoids turning ordinary single words such as ``data`` or ``main``
    # into transliteration merely because their letters happen to be valid MdC.
    return len(token) <= 3 and "a" in token


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
    """Parse Egyptological transliteration and return canonical Unicode.

    The parser understands core MdC shortcuts, common aleph/ayin variants,
    historical Unicode encodings of Egyptological yod, decomposed Unicode,
    editorial punctuation, and mixed prose. Characters it cannot identify
    safely are preserved unchanged.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = _canonicalize_legacy_yod(text)
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
