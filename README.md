# egypttranslit

[![PyPI](https://img.shields.io/pypi/v/egypttranslit?style=flat-square&logo=pypi&logoColor=white&label=PyPI&color=3775A9)](https://pypi.org/project/egypttranslit/)

Convert Egyptological transliteration to clean Unicode with Python or from the command line.

By default, egypttranslit uses the plain-text IFAO-style forms `ȝ`, `ʿ` and `ỉ`.

## Install

```bash
python -m pip install egypttranslit
```

Python 3.10+.

## Try it in 30 seconds

```python
from egypttranslit import parse, parse_mdc, normalize_unicode

print(parse("nTr mAat"))
# nṯr mȝʿt

print(parse_mdc("nTr Htp xpr"))
# nṯr ḥtp ḫpr

print(normalize_unicode("ȝ ʿ ỉ"))
# ꜣ ꜥ ꞽ
```

## What can it do?

| Feature | Example | Result |
| --- | --- | --- |
| Automatic conversion | `parse("nTr mAat")` | `nṯr mȝʿt` |
| Explicit MdC conversion | `parse_mdc("Htp xpr")` | `ḥtp ḫpr` |
| Canonical Unicode | `normalize_unicode("ȝ ʿ ỉ")` | `ꜣ ꜥ ꞽ` |
| Output profiles | `parse_mdc_profiled("mAat", profile="unicode-canonical")` | `mꜣꜥt` |
| Batch conversion | `parse_mdc_many(["nTr", "mAat"])` | `("nṯr", "mȝʿt")` |
| Profiled batch conversion | `parse_mdc_profiled_many(["mAat"], profile="unicode-canonical")` | `("mꜣꜥt",)` |
| Diagnostics | `analyze("mAat", mode="mdc")` | structured result |
| Validation | `validate("mAꜥt")` | raises `ValueError` |
| Command line | `egypttranslit --mode mdc "nTr Htp"` | `nṯr ḥtp` |

## Automatic conversion

Use `parse()` when the input may already contain normal text or Unicode transliteration.

```python
from egypttranslit import parse

assert parse("nTr mAat") == "nṯr mȝʿt"
assert parse("A taxi on the X axis.") == "A taxi on the X axis."
```

`parse()` is conservative: ambiguous ASCII is left unchanged instead of being guessed.

`convert()` is an alias for `parse()`.

## Explicit Manuel de Codage

Use `parse_mdc()` when you know the input is MdC transliteration.

```python
from egypttranslit import parse_mdc

assert parse_mdc("A a H x X S T D") == "ȝ ʿ ḥ ḫ ẖ š ṯ ḏ"
assert parse_mdc("nTr Htp xpr mAat") == "nṯr ḥtp ḫpr mȝʿt"
```

Gardiner/JSesh sign identifiers such as `A1`, `D36` and `T3` are preserved.

## IFAO-style text

The default output uses `ȝ`, `ʿ` and `ỉ` instead of the raised-looking `ꜣ`, `ꜥ` and `ꞽ` glyphs.

Already-transliterated IFAO-style text stays stable:

```python
from egypttranslit import parse

text = "ḏd-ḥr mȝʿ-ḫrw sȝ n ʿnḫ-ḥr"
assert parse(text) == text
```

## Output profiles

Use a profile when you want a specific editorial convention.

```python
from egypttranslit.converter import parse_mdc_profiled

assert parse_mdc_profiled("mAat", profile="ifao") == "mȝʿt"
assert parse_mdc_profiled("mAat", profile="unicode-canonical") == "mꜣꜥt"
assert parse_mdc_profiled("jr qd", profile="gardiner-1957") == "ꞽr ḳd"
```

Available profiles:

| Profile | Main behavior |
| --- | --- |
| `default` | same as `ifao` |
| `ifao` | plain-text `ȝ`, `ʿ`, `ỉ` |
| `unicode-canonical` | canonical `ꜣ`, `ꜥ`, `ꞽ` |
| `gardiner-1957` | Gardiner-style `j → ꞽ`, `q → ḳ` |
| `legacy-diacritics` | alias of `gardiner-1957` |

## Batch conversion

Use `parse_mdc_many()` for the default IFAO-style output:

```python
from egypttranslit.batch import parse_mdc_many

result = parse_mdc_many(["nTr", "Htp", "mAat"])
assert result == ("nṯr", "ḥtp", "mȝʿt")
```

Use `parse_mdc_profiled_many()` when the whole batch should use a specific output profile:

```python
from egypttranslit.batch import parse_mdc_profiled_many

texts = ["mAat", "jr qd"]

assert parse_mdc_profiled_many(
    texts,
    profile="ifao",
) == ("mȝʿt", "jr qd")

assert parse_mdc_profiled_many(
    texts,
    profile="unicode-canonical",
) == ("mꜣꜥt", "jr qd")

assert parse_mdc_profiled_many(
    texts,
    profile="gardiner-1957",
) == ("mꜣꜥt", "ꞽr ḳd")
```

Batch helpers preserve order and accept lists, tuples and generators.

## Diagnostics and validation

```python
from egypttranslit.diagnostics import analyze, validate

result = analyze("mAat", mode="mdc")
assert result.text == "mȝʿt"
assert result.detected == "mdc"

validate("mAꜥt")  # raises ValueError: mixed encoding
```

Diagnostics can classify input as `mdc`, `unicode`, `mixed`, `ambiguous` or `none`.

## Command line

```bash
egypttranslit "nTr mAat"
# nṯr mȝʿt

egypttranslit --mode mdc "nTr Htp xpr"
# nṯr ḥtp ḫpr

egypttranslit --mode mdc --profile unicode-canonical "nTr mAat"
# nṯr mꜣꜥt
```

For files or pipelines:

```bash
cat input.txt | egypttranslit --mode mdc > output.txt
```

Modes: `auto`, `mdc`, `unicode`.

## Main API

```text
parse(text)                                  automatic, conservative conversion
convert(text)                                alias for parse()
parse_mdc(text)                              explicit MdC conversion
normalize_unicode(text)                      canonical Unicode normalization
parse_mdc_profiled(text, profile)            explicit output profile
parse_mdc_many(texts)                        batch MdC conversion
parse_mdc_profiled_many(texts, profile)      batch MdC conversion with an output profile
analyze(text, mode=...)                      diagnostics
validate(text)                               reject dangerous mixed encodings
```

## Citation

Citation metadata is in `CITATION.cff`.

> Barrios, E. J. *egypttranslit* [Computer software]. https://github.com/edujbarrios/egypttranslit

## References

- IFAO: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- Unicode UAX #57: https://unicode.org/reports/tr57/

## License

Apache-2.0. See `LICENSE` and `NOTICE`.
