# egypttranslit

A small Python library for converting Egyptological transliteration into clean Unicode.

It is intended for researchers, digital-humanities projects and small scripts that need to turn common Manuel de Codage-style transliteration into Unicode without configuring a larger conversion system.

## Install

Clone the repository and install it locally:

```bash
git clone https://github.com/edujbarrios/egypttranslit.git
cd egypttranslit
python -m pip install -e .
```

## Usage

For normal use, `parse()` conservatively detects Egyptological transliteration:

```python
from egypttranslit import parse

parse("nTr Htp")
# 'nṯr ḥtp'
```

`convert()` is an alias for `parse()`.

If you already know that the input is Manuel de Codage, use `parse_mdc()`. This avoids ambiguity with ordinary Latin text:

```python
from egypttranslit import parse_mdc

parse_mdc("ra nfr")
```

For text that is already in Egyptological Unicode, `normalize_unicode()` only repairs verified Unicode equivalents and does not interpret ASCII as MdC.

Unknown characters, punctuation, whitespace and hieroglyphs are preserved. Editorial alternatives such as `j` versus Egyptological yod and `q` versus `ḳ` are not guessed automatically.

## Citation

If you use `egypttranslit` in research or scholarly software, please cite it. The repository also contains a `CITATION.cff` file.

For LaTeX/BibTeX:

```bibtex
@misc{barrios2026egypttranslit,
  author       = {Eduardo J. Barrios},
  title        = {egypttranslit},
  year         = {2026},
  version      = {0.5.0},
  howpublished = {\url{https://github.com/edujbarrios/egypttranslit}},
  note         = {ORCID: 0009-0004-7805-6386}
}
```

Then cite it with:

```latex
\cite{barrios2026egypttranslit}
```

## References

The conversion rules and Unicode handling in this project were checked against:

- Institut français d’archéologie orientale (IFAO), **Polices de caractères**: https://www.ifao.egnet.net/publications/publier/outils-ed/polices/
- Institut français d’archéologie orientale (IFAO), **Convertisseurs vers Unicode**: https://www.ifao.egnet.net/publications/publier/outils-ed/convertisseurs/
- IFAO / Sorbonne Université / BnF, **Papyrus Prisse** transliteration corpus: https://prisse.ifao.egnet.net/verse
- Egyptologists' Electronic Forum (EEF), **Transliteration**: https://www.egyptologyforum.org/EEFTransl.html
- Unicode Consortium, **Characters and Combining Marks — Egyptological Yod**: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

## License

Apache-2.0. Attribution information is provided in `NOTICE` and citation metadata in `CITATION.cff`.
