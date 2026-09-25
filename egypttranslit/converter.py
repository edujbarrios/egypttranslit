"""Minimal Egyptological transliteration to Unicode conversion."""

from __future__ import annotations

import unicodedata

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
    }
)


def parse(text: str) -> str:
    """Convert core MdC transliteration shortcuts to normalized Unicode.

    Characters outside the known mapping are preserved unchanged.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    return unicodedata.normalize("NFC", text.translate(_TRANSLATION))


def convert(text: str) -> str:
    """Alias for :func:`parse`."""
    return parse(text)
