# Egyptological Transliteration Converter — Python

A small Python library for turning Egyptological transliteration into clean Unicode.

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

The parser converts the core Manuel de Codage shortcuts:

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

It also understands two common textual variants:

- `3` as an aleph inside MdC transliteration, converted to `ꜣ`.
- IFAO-style Unicode `ȝ` and `ʿ`, canonicalized to `ꜣ` and `ꜥ`.

The returned string is normalized to Unicode NFC.

## Conservative parsing

The parser is designed not to damage surrounding prose. It recognizes whether a token looks like Egyptological transliteration before applying the MdC substitutions.

```python
parse("The word mAat is often discussed in Egyptology.")
# 'The word mꜣꜥt is often discussed in Egyptology.'

parse("Example data stays exactly as written.")
# 'Example data stays exactly as written.'
```

Editorial punctuation is preserved:

```python
parse("[mAat].nTr-Htp=sn <xpr>")
# '[mꜣꜥt].nṯr-ḥtp=sn <ḫpr>'
```

Whitespace, line breaks, unknown characters, hieroglyphs, catalogue numbers, and unsupported notation are kept unchanged. Decomposed Unicode sequences are normalized safely.

The package deliberately uses the dedicated Unicode Egyptological letters `ꜣ` and `ꜥ` rather than exposing multiple output conventions.

## Legacy fonts

Historical fonts such as IFAOtimes, METimes, TranslitAncien, EgyptoRom-Ita, and Transliteration are a different problem from MdC text: a Python `str` does not carry the font that originally gave its code points meaning. The IFAO converter therefore asks the user to choose the original font before conversion.

This package will only add those legacy profiles when their mappings can be independently verified and covered by tests. It will not guess legacy-font equivalences from visual similarity.

Reference material used to define current behavior:

- IFAO, “Polices de caractères”: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- IFAO, “Convertisseurs vers Unicode”: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- Egyptologists' Electronic Forum transliteration table: https://egyptologyforum.org/EEFTransl.html

## Tests

The test suite uses only Python's standard library:

```bash
python -m unittest discover -s tests
```

CI checks Python 3.9, 3.11, and 3.13.

## License

MIT © 2026 Eduardo J. Barrios.
