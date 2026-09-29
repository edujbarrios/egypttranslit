"""Optional transliteration output profiles.

Profiles are deliberately opt-in.  The default MdC conversion keeps editorial
alternatives such as ``j`` and ``q`` unchanged; callers that need a legacy
fully-diacritic output can request it explicitly.
"""

from __future__ import annotations

from typing import Final, Literal

TransliterationProfile = Literal["default", "legacy-diacritics"]

_PROFILES: Final[dict[TransliterationProfile, dict[int, str]]] = {
    "default": {},
    "legacy-diacritics": str.maketrans({"j": "ꞽ", "q": "ḳ"}),
}


def apply_profile(text: str, profile: TransliterationProfile) -> str:
    """Apply one explicit output profile to already-tokenized MdC text."""
    try:
        table = _PROFILES[profile]
    except KeyError as exc:
        supported = ", ".join(sorted(_PROFILES))
        message = (
            f"unknown transliteration profile {profile!r}; "
            f"expected one of: {supported}"
        )
        raise ValueError(message) from exc
    return text.translate(table)
