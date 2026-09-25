# egypttranslit

A small Python library for turning Egyptological transliteration into clean, canonical Unicode.

The API is intentionally tiny:

```python
from egypttranslit import parse

result = parse("nTr Htp xpr m mAat")

# Exact expected value, written with Unicode escapes so this documentation
# does not depend on the font used by GitHub or your browser:
assert result == "n\u1E6Fr \u1E25tp \u1E2Bpr m m\uA723\uA725t"
```

There is no configuration object and there are no runtime dependencies.

> **Unicode display note**
>
> Some Egyptological characters are not present in every monospace font. In particular, the dedicated Egyptological alef, ain and yod may display as empty boxes or with fallback glyphs on some systems. For that reason this README identifies specialist characters by their **Unicode code point** and **Python escape**. Those values are authoritative even when a local font cannot display the glyph correctly.

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

result = parse("nTr Htp")
assert result == "n\u1E6Fr \u1E25tp"
```

`convert()` is an alias:

```python
from egypttranslit import convert

result = convert("mAat")
assert result == "m\uA723\uA725t"
```

## What it understands

### Manuel de Codage shortcuts

The table uses Unicode code points instead of relying on specialist glyph rendering.

| MdC | Unicode code point | Python escape |
| --- | --- | --- |
| `A` | `U+A723` — LATIN SMALL LETTER EGYPTOLOGICAL ALEF | `\uA723` |
| `a` | `U+A725` — LATIN SMALL LETTER EGYPTOLOGICAL AIN | `\uA725` |
| `H` | `U+1E25` — LATIN SMALL LETTER H WITH DOT BELOW | `\u1E25` |
| `x` | `U+1E2B` — LATIN SMALL LETTER H WITH BREVE BELOW | `\u1E2B` |
| `X` | `U+1E96` — LATIN SMALL LETTER H WITH LINE BELOW | `\u1E96` |
| `S` | `U+0161` — LATIN SMALL LETTER S WITH CARON | `\u0161` |
| `T` | `U+1E6F` — LATIN SMALL LETTER T WITH LINE BELOW | `\u1E6F` |
| `D` | `U+1E0F` — LATIN SMALL LETTER D WITH LINE BELOW | `\u1E0F` |

`3` is also understood as an aleph when it appears inside an MdC token and is converted to `U+A723` (`\uA723`).

### Historical Unicode variants

Older or mixed Egyptological data is canonicalized where the equivalence is clear:

| Input representation | Canonical output |
| --- | --- |
| `U+021D` (LATIN SMALL LETTER YOGH) | `U+A723` (EGYPTOLOGICAL ALEF) |
| `U+02BF` (MODIFIER LETTER LEFT HALF RING) | `U+A725` (EGYPTOLOGICAL AIN) |
| `U+1EC9` (LATIN SMALL LETTER I WITH HOOK ABOVE) | `U+A7BD` (LATIN SMALL LETTER GLOTTAL I / Egyptological yod) |
| `U+0069 U+0313` | `U+A7BD` |
| `U+0069 U+0357` | `U+A7BD` |
| `U+0069 U+0486` | `U+A7BD` |

Unicode 12.0 introduced `U+A7BD LATIN SMALL LETTER GLOTTAL I` as the dedicated character used for Egyptological yod. The Unicode Consortium documents it as the preferred representation and notes that the older combining sequences are not automatically normalized to it.

Reference: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

For reference, the three specialist lowercase characters used by the library are:

- Egyptological alef: `U+A723` / Python `\uA723`
- Egyptological ain: `U+A725` / Python `\uA725`
- Egyptological yod: `U+A7BD` / Python `\uA7BD`

## Conservative parsing

`egypttranslit` tries to convert transliteration without damaging surrounding prose.

```python
parse("The word mAat is often discussed in Egyptology.")
# The Egyptological token is converted while the surrounding English remains unchanged.

parse("Example data stays exactly as written.")
# 'Example data stays exactly as written.'
```

Editorial punctuation, whitespace, line breaks, unknown characters, hieroglyphs and catalogue numbers are preserved. The result is normalized to Unicode NFC, and parsing is idempotent: parsing an already converted result does not change it again.

The package does not silently change editorial choices such as `j` versus `U+A7BD` or `q` versus `U+1E33` when both are valid transliteration conventions.

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

## Citation

If you use `egypttranslit` in research, publications or scholarly software, please cite the project using the repository's `CITATION.cff` metadata.

Author: **Eduardo J. Barrios**  
ORCID: `0009-0004-7805-6386`  
GitHub: `https://github.com/edujbarrios`  
Website: `https://edujbarrios.com`

## License and attribution

`egypttranslit` is licensed under the **Apache License 2.0**.

Copyright © 2026 Eduardo J. Barrios.

Redistributions and derivative works must comply with Apache-2.0, including preservation of applicable copyright and attribution notices. This repository includes a `NOTICE` file identifying Eduardo J. Barrios as the author and maintainer; attribution from that file must be preserved where required by Section 4(d) of the license.

See `LICENSE`, `NOTICE` and `CITATION.cff` for the complete licensing and citation metadata.
