"""Optional transliteration output profiles loaded from package data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Final, Literal, TypedDict, cast

TransliterationProfile = Literal[
    "default",
    "ifao",
    "unicode-canonical",
    "gardiner-1957",
    "legacy-diacritics",
]


class _ProfileSpec(TypedDict, total=False):
    mapping: dict[str, str]
    alias: TransliterationProfile
    description: str
    source: str


@dataclass(frozen=True, slots=True)
class ProfileInfo:
    """Read-only metadata describing one transliteration profile."""

    name: TransliterationProfile
    description: str
    source: str | None
    alias_of: TransliterationProfile | None
    mapping: tuple[tuple[str, str], ...]


def _load_profile_specs() -> dict[str, _ProfileSpec]:
    resource = files("egypttranslit").joinpath("data/profiles.json")
    payload = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("invalid transliteration profile data")
    return cast(dict[str, _ProfileSpec], payload)


_PROFILE_SPECS: Final = _load_profile_specs()
TRANSLITERATION_PROFILES: Final[tuple[TransliterationProfile, ...]] = (
    "default",
    "ifao",
    "unicode-canonical",
    "gardiner-1957",
    "legacy-diacritics",
)


def _resolve_profile(profile: TransliterationProfile) -> _ProfileSpec:
    try:
        spec = _PROFILE_SPECS[profile]
    except KeyError as exc:
        supported = ", ".join(TRANSLITERATION_PROFILES)
        raise ValueError(
            f"unknown transliteration profile {profile!r}; expected one of: {supported}"
        ) from exc

    alias = spec.get("alias")
    if alias is None:
        return spec
    try:
        return _PROFILE_SPECS[alias]
    except KeyError as exc:  # pragma: no cover - package data integrity guard
        raise RuntimeError(
            f"profile {profile!r} refers to unknown alias {alias!r}"
        ) from exc


def get_profile_info(profile: TransliterationProfile) -> ProfileInfo:
    """Return documented metadata for one supported transliteration profile."""
    try:
        spec = _PROFILE_SPECS[profile]
    except KeyError as exc:
        supported = ", ".join(TRANSLITERATION_PROFILES)
        raise ValueError(
            f"unknown transliteration profile {profile!r}; expected one of: {supported}"
        ) from exc

    resolved = _resolve_profile(profile)
    alias = spec.get("alias")
    return ProfileInfo(
        name=profile,
        description=spec.get("description", ""),
        source=spec.get("source", resolved.get("source")),
        alias_of=alias,
        mapping=tuple(sorted(resolved.get("mapping", {}).items())),
    )


def list_profile_info() -> tuple[ProfileInfo, ...]:
    """Return metadata for all supported profiles in stable CLI/API order."""
    return tuple(get_profile_info(profile) for profile in TRANSLITERATION_PROFILES)


def apply_profile(text: str, profile: TransliterationProfile) -> str:
    """Apply one explicit output profile to already-tokenized MdC text."""
    spec = _resolve_profile(profile)
    mapping = spec.get("mapping", {})
    translation = str.maketrans(cast(dict[str, str | int | None], mapping))
    return text.translate(translation)
