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

```python
from egypttranslit import parse

parse("nTr Htp")
# 'nṯr ḥtp'
```

A longer example:

```python
from egypttranslit import parse

parse("nTr Htp xpr m mAat")
# equivalent to: "n\u1E6Fr \u1E25tp \u1E2Bpr m m\uA723\uA725t"
```

The Unicode escapes above are used for characters that may not render correctly in every font.

`convert()` is available as an alias for `parse()`:

```python
from egypttranslit import convert

convert("Htp")
# 'ḥtp'
```

The parser also accepts already-Unicode Egyptological text and normalizes older representations where a safe equivalent is known. Unknown characters, punctuation, whitespace and hieroglyphs are preserved.

## Citation

If you use `egypttranslit` in research or scholarly software, please cite it. The repository also contains a `CITATION.cff` file.

For LaTeX/BibTeX:

```bibtex
@misc{barrios2026egypttranslit,
  author       = {Eduardo J. Barrios},
  title        = {egypttranslit},
  year         = {2026},
  version      = {0.4.1},
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
- Egyptologists' Electronic Forum (EEF), **Transliteration**: https://www.egyptologyforum.org/EEFTransl.html
- Unicode Consortium, **Characters and Combining Marks — Egyptological Yod**: https://www.unicode.org/faq/char_combmark.html#Q_Egyptological_Yod

## License

Apache-2.0. Attribution information is provided in `NOTICE` and citation metadata in `CITATION.cff`.
