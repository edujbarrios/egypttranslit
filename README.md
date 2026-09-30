# egypttranslit

[![PyPI](https://img.shields.io/pypi/v/egypttranslit?style=flat-square&logo=pypi&logoColor=white&label=PyPI&color=3775A9)](https://pypi.org/project/egypttranslit/)

A small Python library for converting Egyptological transliteration into clean Unicode.

It is intended for researchers, digital-humanities projects and scripts that need reliable Manuel de Codage-style transliteration conversion without a larger toolchain.

Starting with **1.1.0**, the default presentation follows the plain-text forms commonly used in IFAO material: `ȝ`, `ʿ` and `ỉ`. This avoids the raised-looking `ꜣ`, `ꜥ` and `ꞽ` glyphs that some fonts render awkwardly.

> A web version built on top of this library for non-technical users is planned for a future release.

## Install

Requires Python 3.10 or newer.

```bash
python -m pip install egypttranslit
```

## Quick guide

| API | Use case | Profile | Example | Result |
| --- | --- | --- | --- | --- |
| `parse(text)` | Conservative automatic detection | IFAO default | `parse("nTr mAat")` | `"nṯr mȝʿt"` |
| `parse_mdc(text)` | Known MdC transliteration | IFAO default | `parse_mdc("nTr Htp xpr")` | `"nṯr ḥtp ḫpr"` |
| `parse_mdc_profiled(text, profile="ifao")` | Explicit IFAO plain-text output | `ifao` | `parse_mdc_profiled("mAat", profile="ifao")` | `"mȝʿt"` |
| `parse_mdc_profiled(text, profile="unicode-canonical")` | Previous 1.0.x canonical glyphs | `unicode-canonical` | `parse_mdc_profiled("mAat", profile="unicode-canonical")` | `"mꜣꜥt"` |
| `parse_mdc_profiled(text, profile="gardiner-1957")` | MdC with Gardiner-style `j/q` output | `gardiner-1957` | `parse_mdc_profiled("jr qd", profile="gardiner-1957")` | `"ꞽr ḳd"` |
| `parse_mdc_many(texts)` | Batch of known MdC strings | IFAO default | `parse_mdc_many(["nTr", "mAat"])` | `("nṯr", "mȝʿt")` |
| `normalize_unicode(text)` | Explicit canonical Unicode normalization | canonical | `normalize_unicode("ȝ ʿ ỉ")` | `"ꜣ ꜥ ꞽ"` |
| `analyze(text, mode=...)` | Detection + diagnostics | selected mode | `analyze("mAat", mode="mdc")` | structured result |
| `validate(text)` | Reject dangerous mixed encodings | none | `validate("mAꜥt")` | raises `ValueError` |

`convert(text)` is an alias for `parse(text)`.

## IFAO-style plain text by default

The default output intentionally uses regular plain-text forms instead of the Unicode Egyptological aleph/ayin characters that can look like superscripts in some fonts.

```python
from egypttranslit import parse, parse_mdc

assert parse("nTr mAat") == "nṯr mȝʿt"
assert parse_mdc("A a H x X S T D") == "ȝ ʿ ḥ ḫ ẖ š ṯ ḏ"
```

Already-transliterated IFAO-style text is stable under the default parser:

```python
from egypttranslit import parse

text = (
    "ḏd-ḥr mȝʿ-ḫrw sȝ n ʿnḫ-ḥr sȝ ỉrỉ-pʿt ḥȝtỉ-ʿ wr ʿȝ n mšwš "
    "ḥȝtỉ-ʿỉmỉ-rȝ ḥmw-nṯr n bȝ-nb-ḏw ḏd-ḥr mwt=f nbt pr šp-n-spdt mȝʿ-ḫr"
)

assert parse(text) == text
```

The HTML entity `&#x20;`, sometimes copied after such text, is just a space entity and is not part of the transliteration itself.

## Automatic conversion

```python
from egypttranslit import parse

assert parse("nTr mAat") == "nṯr mȝʿt"
assert parse("A taxi on the X axis.") == "A taxi on the X axis."
```

`parse()` is intentionally conservative: ambiguous ASCII is preserved rather than guessed.

## Explicit MdC

```python
from egypttranslit import parse_mdc

assert parse_mdc("nTr Htp xpr mAat") == "nṯr ḥtp ḫpr mȝʿt"
assert parse_mdc("A1-nTr-D36-Htp-T3") == "A1-nṯr-D36-ḥtp-T3"
```

Common default mappings:

| MdC | IFAO-style Unicode | MdC | IFAO-style Unicode |
| --- | --- | --- | --- |
| `A` | `ȝ` | `a` | `ʿ` |
| `H` | `ḥ` | `x` | `ḫ` |
| `X` | `ẖ` | `S` | `š` |
| `T` | `ṯ` | `D` | `ḏ` |
| `3` | `ȝ` | | |

Gardiner/JSesh sign identifiers such as `A1`, `D36` and `T3` are preserved.

## Canonical Unicode when you need it

The IFAO-style default is a presentation choice. The library still supports the canonical Egyptological Unicode characters explicitly.

For already-Unicode text, use `normalize_unicode()`:

```python
from egypttranslit import normalize_unicode

assert normalize_unicode("ȝ ʿ ỉ") == "ꜣ ꜥ ꞽ"
```

For known MdC input, use the `unicode-canonical` profile to reproduce the 1.0.x output convention without rewriting plain `j` or `q`:

```python
from egypttranslit.converter import parse_mdc_profiled

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="unicode-canonical",
) == "jr qd nṯr mꜣꜥt"
```

## Batch conversion

Use the batch helpers when each transliteration is a separate record. They preserve input order and return a tuple. Lists, tuples and generators are accepted.

```python
from egypttranslit.batch import parse_mdc_many, parse_mdc_profiled_many

texts = ["nTr Htp", "xpr mAat", "jr qd"]

assert parse_mdc_many(texts) == (
    "nṯr ḥtp",
    "ḫpr mȝʿt",
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

`parse_many()` and `normalize_unicode_many()` provide the same batch behavior for conservative automatic parsing and canonical Unicode normalization.

## Profiles

The default behavior uses IFAO-style `ȝ`, `ʿ` and `ỉ`, while leaving plain `j` and `q` unchanged because editorial conventions differ.

| Profile | Behavior | Notes |
| --- | --- | --- |
| `default` | same as `ifao` | default since 1.1.0 |
| `ifao` | `ꜣ → ȝ`, `ꜥ → ʿ`, `ꞽ → ỉ` (and uppercase equivalents) | plain-text IFAO-style presentation |
| `unicode-canonical` | keeps canonical `ꜣ`, `ꜥ`, `ꞽ`; preserves `j` and `q` | compatibility path for 1.0.x MdC output |
| `gardiner-1957` | `j → ꞽ`, `q → ḳ` | Gardiner-style output described in Unicode UAX #57 |
| `legacy-diacritics` | same as `gardiner-1957` | backward-compatible alias |

```python
from egypttranslit.converter import parse_mdc_profiled

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="default",
) == "jr qd nṯr mȝʿt"

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="ifao",
) == "jr qd nṯr mȝʿt"

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="gardiner-1957",
) == "ꞽr ḳd nṯr mꜣꜥt"
```

Profile metadata can be inspected programmatically:

```python
from egypttranslit.profiles import get_profile_info, list_profile_info

info = get_profile_info("ifao")
assert ("ꜣ", "ȝ") in info.mapping
assert info.alias_of is None

available = tuple(profile.name for profile in list_profile_info())
# ("default", "ifao", "unicode-canonical", "gardiner-1957", "legacy-diacritics")
```

## Diagnostics

```python
from egypttranslit.diagnostics import analyze, validate

result = analyze("mAat", mode="mdc")
assert result.text == "mȝʿt"
assert result.detected == "mdc"
assert result.warnings == ()

validate("mAꜥt")  # raises ValueError
```

`detected` is one of `mdc`, `unicode`, `mixed`, `ambiguous` or `none`. `confidence` is a deterministic heuristic score, not a philological probability.

## Command line

```bash
egypttranslit "nTr mAat"
# nṯr mȝʿt

egypttranslit --mode mdc "nTr Htp xpr"
# nṯr ḥtp ḫpr

egypttranslit --mode mdc --profile unicode-canonical "nTr mAat"
# nṯr mꜣꜥt

egypttranslit --mode mdc --profile gardiner-1957 "jr qd nTr"
# ꞽr ḳd nṯr

egypttranslit --mode unicode "ȝ ʿ ỉ"
# ꜣ ꜥ ꞽ
```

For pipelines:

```bash
cat input.txt | egypttranslit --mode mdc > output.txt
```

Modes are `auto` (default IFAO-style output), `mdc` and `unicode` (canonical normalization). Non-default profiles are valid only with `--mode mdc`.

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
