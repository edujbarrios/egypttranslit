# egypttranslit

A small Python library for converting Egyptological transliteration into clean Unicode.

It is intended for researchers, digital-humanities projects and small scripts that need to turn common Manuel de Codage-style transliteration into Unicode without configuring a larger conversion system.

## Install

Requires Python 3.10 or newer.

For a published release, install from PyPI:

```bash
python -m pip install egypttranslit
```

For development or unreleased changes, install from a local clone:

```bash
git clone https://github.com/edujbarrios/egypttranslit.git
cd egypttranslit
python -m pip install -e .
```

## Quick guide

The library deliberately separates **automatic detection**, **explicit MdC conversion**, **editorial profiles**, and **already-Unicode normalization** so callers can choose how much interpretation they want.

| API | Input type / mode | Profile | Example | Result |
| --- | --- | --- | --- | --- |
| `parse(text)` | Conservative automatic detection (`auto`) | implicit `default` | `parse("nTr mAat")` | `"nṯr mꜣꜥt"` |
| `parse_mdc(text)` | Explicit Manuel de Codage transliteration (`mdc`) | `default` | `parse_mdc("nTr Htp xpr mAat")` | `"nṯr ḥtp ḫpr mꜣꜥt"` |
| `parse_mdc_profiled(text, profile="default")` | Explicit MdC | `default` | `parse_mdc_profiled("jr qd", profile="default")` | `"jr qd"` |
| `parse_mdc_profiled(text, profile="gardiner-1957")` | Explicit MdC | `gardiner-1957` | `parse_mdc_profiled("jr qd", profile="gardiner-1957")` | `"ꞽr ḳd"` |
| `parse_mdc_profiled(text, profile="legacy-diacritics")` | Explicit MdC | compatibility alias | `parse_mdc_profiled("jr qd", profile="legacy-diacritics")` | `"ꞽr ḳd"` |
| `normalize_unicode(text)` | Already-Unicode Egyptological text (`unicode`) | none | `normalize_unicode("ȝ ʿ ỉ")` | canonical Egyptological Unicode |
| `analyze(text, mode=...)` | Diagnostic conversion | follows selected mode | `analyze("mAat", mode="mdc")` | structured result + detection/warnings |
| `validate(text)` | Validation only | none | `validate("mAꜥt")` | raises on dangerous mixed encoding |

`convert(text)` is an alias for the conservative `parse(text)` entry point.

### Automatic conversion

Use `parse()` when input may contain ordinary text mixed with transliteration and you do **not** want the library to guess aggressively:

```python
from egypttranslit import parse

assert parse("nTr mAat") == "nṯr mꜣꜥt"
assert parse("A taxi on the X axis.") == "A taxi on the X axis."
```

`parse()` converts tokens only when the input contains sufficiently distinctive MdC evidence. Ambiguous ASCII is preserved rather than guessed.

### Explicit Manuel de Codage (MdC)

Use `parse_mdc()` when the input is known to be MdC transliteration. This mode applies the full transliteration character mapping while preserving layout punctuation and protected sign identifiers:

```python
from egypttranslit import parse_mdc

assert parse_mdc("nTr Htp xpr mAat") == "nṯr ḥtp ḫpr mꜣꜥt"
assert parse_mdc("A1-nTr-D36-Htp-T3") == "A1-nṯr-D36-ḥtp-T3"
```

Typical MdC mappings include:

| MdC | Unicode | MdC | Unicode |
| --- | --- | --- | --- |
| `A` | `ꜣ` | `a` | `ꜥ` |
| `H` | `ḥ` | `x` | `ḫ` |
| `X` | `ẖ` | `S` | `š` |
| `T` | `ṯ` | `D` | `ḏ` |
| `3` | `ꜣ` | | |

Gardiner/JSesh sign identifiers such as `A1`, `D36` and `T3` are protected and are not mistaken for transliteration tokens.

### Already-Unicode text

Use `normalize_unicode()` when the source already contains scholarly Unicode and only canonical normalization / supported historical-form normalization is desired:

```python
from egypttranslit import normalize_unicode

result = normalize_unicode("ȝ ʿ ỉ")
```

## Explicit transliteration profiles

The stable package-level `parse_mdc(text)` uses the `default` editorial behavior and intentionally preserves plain `j` and `q`. Applications that need a specific output convention can opt into `parse_mdc_profiled()`.

| Profile | Intended use | Additional mapping | Notes |
| --- | --- | --- | --- |
| `default` | Conservative explicit MdC conversion | none for `j` / `q` | Preserves `j` and `q` because editorial conventions differ. |
| `gardiner-1957` | Explicit Gardiner-style output | `j → ꞽ`, `q → ḳ` | Matches the Gardiner 1957 transliteration repertoire described by Unicode UAX #57. |
| `legacy-diacritics` | Backward compatibility | same as `gardiner-1957` | Alias retained so existing callers do not break. |

Example using the default profile:

```python
from egypttranslit.converter import parse_mdc_profiled

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="default",
) == "jr qd nṯr mꜣꜥt"
```

The same MdC with the Gardiner 1957 profile:

```python
from egypttranslit.converter import parse_mdc_profiled

assert parse_mdc_profiled(
    "jr qd nTr mAat",
    profile="gardiner-1957",
) == "ꞽr ḳd nṯr mꜣꜥt"
```

The `legacy-diacritics` alias produces the same output:

```python
assert parse_mdc_profiled(
    "jr qd",
    profile="legacy-diacritics",
) == "ꞽr ḳd"
```

The profile definitions live in `egypttranslit/data/profiles.json` rather than being embedded in conversion logic, so mappings can be reviewed and extended independently. No single `ifao` profile is imposed because the IFAO explicitly documents alternatives such as `j` or `ỉ` and `q` or `ḳ`; choosing between those remains an explicit editorial decision.

Applications can inspect the available profiles programmatically:

```python
from egypttranslit.profiles import get_profile_info, list_profile_info

info = get_profile_info("gardiner-1957")
assert info.mapping == (("j", "ꞽ"), ("q", "ḳ"))
assert info.alias_of is None

available = tuple(profile.name for profile in list_profile_info())
# ("default", "gardiner-1957", "legacy-diacritics")
```

`ProfileInfo` also exposes the human-readable description and documented source for a profile. Alias profiles retain their alias relationship while reporting the resolved mapping and source.

## Diagnostics and validation

For ingestion pipelines, corpora and research tooling that need to inspect input before accepting a conversion, use the opt-in diagnostic API:

```python
from egypttranslit.diagnostics import analyze, validate

result = analyze("mAat", mode="mdc")
assert result.text == "mꜣꜥt"
assert result.detected == "mdc"
assert result.confidence == 0.9
assert result.warnings == ()

validate("mAꜥt")  # raises ValueError: mixed ASCII/Unicode token
```

`ConversionResult.detected` is one of `mdc`, `unicode`, `mixed`, `ambiguous` or `none`. `confidence` is a deterministic heuristic score describing the strength of the character evidence; it is **not** a statistical probability and should not be interpreted as philological certainty. Sign identifiers are excluded from this detection logic, and mixed ASCII/Unicode transliteration inside one token is reported explicitly.

A practical ingestion workflow can therefore validate first and then convert explicitly:

```python
from egypttranslit.converter import parse_mdc_profiled
from egypttranslit.diagnostics import validate

source = "jr qd nTr mAat"
validate(source)
clean = parse_mdc_profiled(source, profile="gardiner-1957")
assert clean == "ꞽr ḳd nṯr mꜣꜥt"
```

## Command line

Installation also provides the `egypttranslit` command. CLI modes correspond directly to the Python workflows above:

| CLI | Meaning |
| --- | --- |
| `egypttranslit TEXT` | conservative automatic conversion (`auto`) |
| `egypttranslit --mode mdc TEXT` | explicit MdC conversion with `default` profile |
| `egypttranslit --mode mdc --profile gardiner-1957 TEXT` | explicit MdC using Gardiner 1957 `j/q` output |
| `egypttranslit --mode mdc --profile legacy-diacritics TEXT` | compatibility alias for Gardiner-style output |
| `egypttranslit --mode unicode TEXT` | normalize already-Unicode scholarly text |

Examples:

```bash
egypttranslit "nTr mAat"
# nṯr mꜣꜥt

egypttranslit --mode mdc "nTr Htp xpr mAat"
# nṯr ḥtp ḫpr mꜣꜥt

egypttranslit --mode mdc --profile gardiner-1957 "jr qd nTr"
# ꞽr ḳd nṯr

egypttranslit --mode unicode "ȝ ʿ ỉ"
```

For files or pipelines, omit the text argument and send input through stdin; whitespace and line breaks are preserved:

```bash
cat input.txt | egypttranslit --mode mdc --profile gardiner-1957 > output.txt
```

The modes are `auto` (default), `mdc` and `unicode`. Non-default profiles are valid only with `--mode mdc`. `egypttranslit --version` prints the installed version.

Unknown characters, punctuation and whitespace are preserved. Encoded Egyptian hieroglyphs are treated as opaque Unicode data: the original Egyptian Hieroglyphs block, Egyptian Hieroglyph Format Controls (including joiners, segment delimiters, mirror/damage controls and variation sequences), and Egyptian Hieroglyphs Extended-A are never interpreted as transliteration. Gardiner/JSesh sign identifiers such as `A1`, `D36` and `T3` are also preserved rather than interpreted as transliteration. Editorial alternatives such as `j` versus Egyptological yod and `q` versus `ḳ` are not guessed automatically.

## Supported API and scope

The supported package-level API is intentionally small and consists of exactly `parse`, `parse_mdc`, `normalize_unicode` and `convert`. Each accepts one Python `str` and returns a plain `str`; non-string inputs raise `TypeError`. `__version__` exposes installed distribution metadata but is not a conversion function.

Advanced opt-in helpers such as `egypttranslit.converter.parse_mdc_profiled`, `egypttranslit.profiles` and `egypttranslit.diagnostics` are intentionally outside the package-level `__all__`, so the stable four-function conversion API remains backward compatible.

The library converts transliteration encodings; it is not a renderer or a general parser for the full Manuel de Codage hieroglyph-layout language. Gardiner/JSesh sign identifiers and encoded hieroglyph formatting remain opaque data. Automatic `parse()` is intentionally conservative and may leave ambiguous ASCII unchanged; callers that know an input is MdC should use `parse_mdc()` instead of relying on detection.

Internal names beginning with `_` are implementation details and are not part of the supported API.

## Release integrity

Release artifacts are built and checked as both wheel and source distribution, installed in isolated environments, and exercised through both the Python API and the installed CLI. Production publishing uses PyPI Trusted Publishing through GitHub OIDC rather than a stored long-lived PyPI token. A separate manual TestPyPI workflow is available for release rehearsals.

Production releases can be initiated from GitHub Actions after the version metadata has been prepared and merged to `main`; the release workflow validates the requested version against the project metadata, publishes to PyPI, and only then creates the matching GitHub tag/release.

Publishing environments (`pypi` and `testpypi`) must be configured as Trusted Publishers on the corresponding package indexes before those workflows can upload a release.

## Citation

Citation metadata is provided in `CITATION.cff`.

> Barrios, E. J. *egypttranslit* [Computer software]. https://github.com/edujbarrios/egypttranslit

## References

The conversion rules and Unicode handling in this project were checked against:

- Institut français d’archéologie orientale (IFAO), **Polices de caractères**: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- Institut français d’archéologie orientale (IFAO), **Convertisseurs vers Unicode**: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- IFAO / Sorbonne Université / BnF, **Papyrus Prisse** transliteration corpus: https://prisse.ifao.egnet.net/verse
- Egyptologists' Electronic Forum (EEF), **Transliteration**: https://www.egyptologyforum.org/EEFTransl.html
- Unicode Consortium, **Characters and Combining Marks — Egyptological Yod**: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod
- Unicode Consortium, **UAX #57: Unicode Egyptian Hieroglyph Database**: https://unicode.org/reports/tr57/
- Unicode Consortium, **Egyptian Hieroglyph Format Controls**: https://www.unicode.org/charts/nameslist/n_13430.html

## License

Apache-2.0. Attribution information is provided in `NOTICE` and citation metadata in `CITATION.cff`.
