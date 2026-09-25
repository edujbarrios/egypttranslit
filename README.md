# Egyptological Transliteration Converter — Python

A small Python library for turning Egyptological transliteration into clean, canonical Unicode.

The public API stays intentionally simple: pass a string to `parse()` and get Unicode back. There is no configuration object and there are no runtime dependencies.

```python
from egyptological_transliteration_converter_python import parse

text = parse("nTr Htp xpr m mAat")
print(text)
# nṯr ḥtp ḫpr m mꜣꜥt
```

## Install

For local development:

```bash
git clone https://github.com/edujbarrios/egyptological-transliteration-converter-python.git
cd egyptological-transliteration-converter-python
python -m pip install -e .
```

A normal local install also works:

```bash
python -m pip install .
```

## Usage

```python
from egyptological_transliteration_converter_python import parse

parse("nTr Htp")
# 'nṯr ḥtp'
```

`convert()` is an alias if that reads better in your code:

```python
from egyptological_transliteration_converter_python import convert

convert("mAat")
# 'mꜣꜥt'
```

The repository, installed distribution, and importable Python package use the same name, with hyphens replaced by underscores where Python syntax requires it.

## What the parser understands

### Manuel de Codage shortcuts

| MdC | Unicode |
| --- | --- |
| `A` | `ꜣ` |
| `a` | `ꜥ` |
| `H` | `ḥ` |
| `x` | `ḫ` |
| `X` | `ẖ` |
| `S` | `š` |
| `T` | `ṯ` |
| `D` | `ḏ` |

`3` is also understood as an aleph when it appears inside an MdC token.

### Historical Unicode variants

The parser also repairs several representations found in older or mixed Egyptological data:

| Input | Canonical output |
| --- | --- |
| `ȝ` | `ꜣ` |
| `ʿ` | `ꜥ` |
| `ỉ` | `ꞽ` |
| `i` + U+0313 | `ꞽ` |
| `i` + U+0357 | `ꞽ` |
| `i` + U+0486 | `ꞽ` |

Unicode 12.0 introduced the dedicated Egyptological yod `ꞽ` (U+A7BD). The Unicode Consortium documents it as the preferred character and notes that the three older combining sequences are not automatically normalized to it.

Reference: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

The returned string is normalized to Unicode NFC after Egyptological canonicalization.

## Conservative parsing

The parser tries to convert transliteration without damaging surrounding prose.

```python
parse("The word mAat is often discussed in Egyptology.")
# 'The word mꜣꜥt is often discussed in Egyptology.'

parse("Example data stays exactly as written.")
# 'Example data stays exactly as written.'

parse("data")
# 'data'
```

Editorial punctuation is preserved:

```python
parse("[mAat].nTr-Htp=sn <xpr>")
# '[mꜣꜥt].nṯr-ḥtp=sn <ḫpr>'
```

Whitespace, line breaks, unknown characters, hieroglyphs, catalogue numbers, and unsupported notation are kept unchanged. Parsing is idempotent: parsing an already converted result does not change it again.

The package deliberately uses the dedicated Unicode Egyptological letters `ꜣ`, `ꜥ`, and `ꞽ` when repairing equivalent historical encodings. It does not silently change editorial choices such as `j` versus `ꞽ` or `q` versus `ḳ` when both are already valid transliteration conventions.

## Legacy fonts

Historical fonts such as IFAOtimes, METimes, TranslitAncien, EgyptoRom-Ita, and Transliteration are a different problem from MdC text: a Python `str` does not carry the font that originally gave its code points meaning. The IFAO converter therefore asks the user to choose the original font before conversion.

This package will only add those legacy profiles when their mappings can be independently verified and covered by tests. It will not guess legacy-font equivalences from visual similarity.

Reference material used to define current behavior:

- IFAO, “Polices de caractères”: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- IFAO, “Convertisseurs vers Unicode”: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- Unicode Consortium, “Egyptological Yod”: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

## Tests

The test suite uses only Python's standard library:

```bash
python -m unittest discover -s tests
```

CI checks Python 3.9, 3.11, and 3.13.

## License

MIT © 2026 Eduardo J. Barrios.
