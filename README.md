# Egyptological Transliteration Converter — Python

A small Python library for converting common Manuel de Codage (MdC) Egyptological transliteration shortcuts into Unicode.

The library is intentionally simple: give it a string and get Unicode back. There is no format selector, no configuration object, and no runtime dependency.

```python
from egypttranslit import parse

text = parse("nTr Htp xpr m mAat")
print(text)
# nṯr ḥtp ḫpr m mꜣꜥt
```

## Install

For local development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/edujbarrios/egyptological-transliteration-converter-python.git
cd egyptological-transliteration-converter-python
pip install -e .
```

A normal local install also works:

```bash
pip install .
```

## Usage

Use `parse()` for the shortest API:

```python
from egypttranslit import parse

parse("nTr Htp")
# 'nṯr ḥtp'
```

`convert()` is an alias if that reads better in your code:

```python
from egypttranslit import convert

convert("mAat")
# 'mꜣꜥt'
```

## Current conversions

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

Characters that are not part of the mapping are kept unchanged. The returned string is normalized to Unicode NFC.

The package deliberately uses the dedicated Unicode Egyptological letters `ꜣ` and `ꜥ` rather than exposing multiple output conventions.

## Scope

This package is the small Python counterpart to the browser-based Egyptological Transliteration Converter. Its goal is to be convenient in scripts, notebooks, data-cleaning pipelines, and research tools.

It currently focuses on the core MdC transliteration shortcuts above. Additional legacy-font mappings should only be added when their character mappings can be documented and tested.

## Tests

The test suite uses only Python's standard library:

```bash
python -m unittest discover -s tests
```

## License

MIT © 2026 Eduardo J. Barrios.
