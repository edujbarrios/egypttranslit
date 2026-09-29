# egypttranslit

[![PyPI version](https://img.shields.io/pypi/v/egypttranslit.svg)](https://pypi.org/project/egypttranslit/)

A small Python library for converting Egyptological transliteration into clean Unicode.

It is intended for researchers, digital-humanities projects and scripts that need reliable Manuel de Codage-style transliteration conversion without a larger toolchain.

> A web version built on top of this library for non-technical users is planned for a future release.

## Install

Requires Python 3.10 or newer.

```bash
python -m pip install egypttranslit
```

## Quick guide

| API | Use case | Profile | Example | Result |
| --- | --- | --- | --- | --- |
| `parse(text)` | Conservative automatic detection | `default` | `parse("nTr mAat")` | `"nṯr mꜣꜥt"` |
| `parse_mdc(text)` | Known MdC transliteration | `default` | `parse_mdc("nTr Htp xpr")` | `"nṯr ḥtp ḫpr"` |
| `parse_mdc_profiled(text, profile="gardiner-1957")` | MdC with Gardiner-style `j/q` output | `gardiner-1957` | `parse_mdc_profiled("jr qd", profile="gardiner-1957")` | `"ꞽr ḳd"` |
| `parse_mdc_many(texts)` | Batch of known MdC strings | `default` | `parse_mdc_many(["nTr", "Htp"])` | `("nṯr", "ḥtp")` |
| `parse_mdc_profiled_many(texts, profile=...)` | Batch MdC with one profile | selected profile | `parse_mdc_profiled_many(["jr qd"], profile="gardiner-1957")` | `("ꞽr ḳd",)` |
| `normalize_unicode(text)` | Already-Unicode scholarly text | none | `normalize_unicode("ȝ ʿ ỉ")` | canonical Unicode |
| `analyze(text, mode=...)` | Detection + diagnostics | selected mode | `analyze("mAat", mode="mdc")` | structured result |
| `validate(text)` | Reject dangerous mixed encodings | none | `validate("mAꜥt")` | raises `ValueError` |

`convert(text)` is an alias for `parse(text)`.

## Examples

### Automatic conversion

```python
from egypttranslit import parse

assert parse("nTr mAat") == "nṯr mꜣꜥt"
assert parse("A taxi on the X axis.") == "A taxi on the X axis."
```

`parse()` is intentionally conservative: ambiguous ASCII is preserved rather than guessed.

### Explicit MdC

```python
from egypttranslit import parse_mdc

assert parse_mdc("nTr Htp xpr mAat") == "nṯr ḥtp ḫpr mꜣꜥt"
assert parse_mdc("A1-nTr-D36-Htp-T3") == "A1-nṯr-D36-ḥtp-T3"
```

Common mappings:

| MdC | Unicode | MdC | Unicode |
| --- | --- | --- | --- |
| `A` | `ꜣ` | `a` | `ꜥ` |
| `H` | `ḥ` | `x` | `ḫ` |
| `X` | `ẖ` | `S` | `š` |
| `T` | `ṯ` | `D` | `ḏ` |
| `3` | `ꜣ` | | |

Gardiner/JSesh sign identifiers such as `A1`, `D36` and `T3` are preserved.

### Batch conversion

Use the batch helpers when each transliteration is a separate record. They preserve input order and return a tuple. Lists, tuples and generators are accepted.

```python
from egypttranslit.batch import parse_mdc_many, parse_mdc_profiled_many

texts = ["nTr Htp", "xpr mAat", "jr qd"]

assert parse_mdc_many(texts) == (
    "nṯr ḥtp",
    "ḫpr mꜣꜥt",
    "jr qd",
)

assert parse_mdc_profiled_many(
    texts,
    profile="gardiner-1957",
) == (
    "nṯr ḥtp",
    "ḫpr mꜣꜥt",
    "ꞽr ḳd",
)
```

`parse_many()` and `normalize_unicode_many()` provide the same batch behavior for conservative automatic parsing and Unicode normalization.

## Profiles

The default behavior intentionally leaves plain `j` and `q` unchanged because editorial conventions differ.

| Profile | Behavior | Notes |
| --- | --- | --- |
| `default` | preserves `j` and `q` | safest general behavior |
| `gardiner-1957` | `j → ꞽ`, `q → ḳ` | Gardiner-style output described in Unicode UAX #57 |
| `legacy-diacritics` | same as `gardiner-1957` | backward-compatible alias |

```python
from egypttranslit.converter import parse_mdc_profiled

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="default",
) == "jr qd nṯr mꜣꜥt"

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="gardiner-1957",
) == "ꞽr ḳd nṯr mꜣꜥt"
```

Profile metadata can be inspected programmatically:

```python
from egypttranslit.profiles import get_profile_info, list_profile_info

info = get_profile_info("gardiner-1957")
assert info.mapping == (("j", "ꞽ"), ("q", "ḳ"))
assert info.alias_of is None

available = tuple(profile.name for profile in list_profile_info())
# ("default", "gardiner-1957", "legacy-diacritics")
```

No single `ifao` profile is imposed because IFAO documents editorial alternatives such as `j` or `ỉ` and `q` or `ḳ`.

## Diagnostics

```python
from egypttranslit.diagnostics import analyze, validate

result = analyze("mAat", mode="mdc")
assert result.text == "mꜣꜥt"
assert result.detected == "mdc"
assert result.warnings == ()

validate("mAꜥt")  # raises ValueError
```

`detected` is one of `mdc`, `unicode`, `mixed`, `ambiguous` or `none`. `confidence` is a deterministic heuristic score, not a philological probability.

## Command line

```bash
egypttranslit "nTr mAat"
# nṯr mꜣꜥt

egypttranslit --mode mdc "nTr Htp xpr"
# nṯr ḥtp ḫpr

egypttranslit --mode mdc --profile gardiner-1957 "jr qd nTr"
# ꞽr ḳd nṯr

egypttranslit --mode unicode "ȝ ʿ ỉ"
```

For pipelines:

```bash
cat input.txt | egypttranslit --mode mdc --profile gardiner-1957 > output.txt
```

Modes are `auto` (default), `mdc` and `unicode`. Non-default profiles are valid only with `--mode mdc`.

## Citation

Citation metadata is provided in `CITATION.cff`.

> Barrios, E. J. *egypttranslit* [Computer software]. https://github.com/edujbarrios/egypttranslit

## References

- Institut français d’archéologie orientale (IFAO), **Polices de caractères**: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- Institut français d’archéologie orientale (IFAO), **Convertisseurs vers Unicode**: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- Unicode Consortium, **UAX #57: Unicode Egyptian Hieroglyph Database**: https://unicode.org/reports/tr57/
- Unicode Consortium, **Egyptian Hieroglyph Format Controls**: https://www.unicode.org/charts/nameslist/n_13430.html

## License

Apache-2.0. Attribution information is provided in `NOTICE` and citation metadata in `CITATION.cff`.
