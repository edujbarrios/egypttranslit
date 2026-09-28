# Changelog

This file records user-visible changes. Citation metadata remains in `CITATION.cff`.

## 0.9.0

- Added the dependency-free `egypttranslit` command with `auto`, `mdc` and `unicode` modes, stdin support and deterministic UTF-8 I/O across Linux, macOS and Windows.
- Preserved multi-digit numeric runs in explicit MdC conversion while retaining `3` as the documented aleph alias in transliteration tokens.
- Made historical Egyptological yod normalization robust to additional and canonically reordered combining marks without discarding unrelated editorial diacritics.
- Hardened wheel/sdist audits, reproducible wheel builds, public API contracts, deterministic Unicode fuzzing and cross-platform CI.
- Pinned GitHub Actions and the Python build/validation toolchain for reproducible release checks.

## 0.8.0

- Protected Gardiner, Hieroglyphica and JSesh sign identifiers from transliteration conversion using Unicode UAX #57 grammars.
- Tightened conservative automatic MdC detection to preserve ambiguous ASCII rather than guessing.
- Added exhaustive contracts for supported Egyptological Unicode, NFC/idempotence and Egyptian hieroglyph/format-control preservation.
- Expanded release validation across Python 3.10–3.14 plus Python-next testing.

## 0.7.0

- Added explicit `parse_mdc()` and `normalize_unicode()` workflows alongside conservative `parse()`.
- Added strict typing, wheel/sdist checks and synchronized release metadata validation.
