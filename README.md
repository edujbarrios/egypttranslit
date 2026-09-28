# egypttranslit

A small Python library for converting Egyptological transliteration into clean Unicode.

It is intended for researchers, digital-humanities projects and small scripts that need to turn common Manuel de Codage-style transliteration into Unicode without configuring a larger conversion system.

## Install

Requires Python 3.10 or newer.

Clone the repository and install it locally:

```bash
git clone https://github.com/edujbarrios/egypttranslit.git
cd egypttranslit
python -m pip install -e .
```

## Quick guide

| Function | Use it when | Example |
| --- | --- | --- |
| `parse(text)` | You want conservative automatic parsing. | `parse("nTr mAat")` |
| `parse_mdc(text)` | You know the input is Manuel de Codage transliteration. | `parse_mdc("nTr Htp xpr")` |
| `normalize_unicode(text)` | The text is already Egyptological Unicode and only needs safe normalization. | `normalize_unicode("ȝ ʿ ỉ")` |
| `convert(text)` | You prefer an alias for `parse()`. | `convert("nTr mAat")` |

For normal use:

```python
from egypttranslit import parse

result = parse("nTr mAat")
```

`parse()` is deliberately conservative. It converts only tokens that carry sufficiently distinctive MdC evidence and never assumes that neighbouring ASCII words are also MdC. Ambiguous input is preserved rather than guessed.

If the input is definitely MdC transliteration, use the explicit mode for complete conversion:

```python
from egypttranslit import parse_mdc

result = parse_mdc("nTr Htp xpr m mAat")
```

For already-Unicode scholarly text:

```python
from egypttranslit import normalize_unicode

result = normalize_unicode(text)
```

Unknown characters, punctuation, whitespace and hieroglyphs are preserved. Gardiner/JSesh sign identifiers such as `A1`, `D36` and `T3` are also preserved rather than interpreted as transliteration. Editorial alternatives such as `j` versus Egyptological yod and `q` versus `ḳ` are not guessed automatically.

## Citation

`CITATION.cff` is the single source of citation metadata for this project.

On GitHub, choose **Cite this repository → BibTeX**, copy the generated entry into your `.bib` file, and cite the key from that entry in LaTeX:

```latex
\cite{<bibtex-key>}
```

Keeping the bibliographic metadata only in `CITATION.cff` avoids duplicated author, ORCID and version information in the README.

## References

The conversion rules and Unicode handling in this project were checked against:

- Institut français d’archéologie orientale (IFAO), **Polices de caractères**: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- Institut français d’archéologie orientale (IFAO), **Convertisseurs vers Unicode**: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- IFAO / Sorbonne Université / BnF, **Papyrus Prisse** transliteration corpus: https://prisse.ifao.egnet.net/verse
- Egyptologists' Electronic Forum (EEF), **Transliteration**: https://www.egyptologyforum.org/EEFTransl.html
- Unicode Consortium, **Characters and Combining Marks — Egyptological Yod**: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod
- Unicode Consortium, **UAX #57: Unicode Egyptian Hieroglyph Database**: https://unicode.org/reports/tr57/

## License

Apache-2.0. Attribution information is provided in `NOTICE` and citation metadata in `CITATION.cff`.
