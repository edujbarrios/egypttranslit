# egypttranslit

A small Python library for turning Egyptological transliteration into clean, canonical Unicode.

The API is intentionally tiny:

```python
from egypttranslit import parse

parse("nTr Htp xpr m mAat")
# 'nṯr ḥtp ḫpr m mꜣꜥt'
```

There is no configuration object and there are no runtime dependencies.

## Install

For local development:

```bash
git clone https://github.com/edujbarrios/egypttranslit.git
cd egypttranslit
python -m pip install -e .
```

A normal local install also works:

```bash
python -m pip install .
```

## Usage

```python
from egypttranslit import parse

parse("nTr Htp")
# 'nṯr ḥtp'
```

`convert()` is an alias:

```python
from egypttranslit import convert

convert("mAat")
# 'mꜣꜥt'
```

## What it understands

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

Older or mixed Egyptological data is canonicalized where the equivalence is clear:

| Input | Canonical output |
| --- | --- |
| `ȝ` | `ꜣ` |
| `ʿ` | `ꜥ` |
| `ỉ` | `ꞽ` |
| `i` + U+0313 | `ꞽ` |
| `i` + U+0357 | `ꞽ` |
| `i` + U+0486 | `ꞽ` |

Unicode 12.0 introduced the dedicated Egyptological yod `ꞽ` (U+A7BD). The Unicode Consortium documents it as the preferred character and notes that the older combining sequences are not automatically normalized to it.

Reference: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

## Conservative parsing

`egypttranslit` tries to convert transliteration without damaging surrounding prose.

```python
parse("The word mAat is often discussed in Egyptology.")
# 'The word mꜣꜥt is often discussed in Egyptology.'

parse("Example data stays exactly as written.")
# 'Example data stays exactly as written.'
```

Editorial punctuation, whitespace, line breaks, unknown characters, hieroglyphs and catalogue numbers are preserved. The result is normalized to Unicode NFC, and parsing is idempotent: parsing an already converted result does not change it again.

The package does not silently change editorial choices such as `j` versus `ꞽ` or `q` versus `ḳ` when both are valid transliteration conventions.

## Legacy fonts

Historical fonts such as IFAOtimes, METimes, TranslitAncien, EgyptoRom-Ita and Transliteration require verified font-specific mappings. Those profiles will only be added when their mappings can be documented and tested; the library does not guess legacy-font equivalences from visual similarity.

References:

- IFAO, “Polices de caractères”: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- IFAO, “Convertisseurs vers Unicode”: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- Unicode Consortium, “Egyptological Yod”: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

## Tests

```bash
python -m unittest discover -s tests
```

CI checks Python 3.9, 3.11 and 3.13.

## License

MIT © 2026 Eduardo J. Barrios.
