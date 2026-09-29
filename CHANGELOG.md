# Changelog

This file records user-visible changes. Citation metadata remains in `CITATION.cff`.

## 0.9.0

- Added the dependency-free `egypttranslit` command with `auto`, `mdc` and `unicode` modes, stdin support, explicit profile selection and deterministic UTF-8 I/O across Linux, macOS and Windows.
- Added declarative transliteration profiles backed by package data, including the explicit `gardiner-1957` convention (`j → ꞽ`, `q → ḳ`) and the backward-compatible `legacy-diacritics` alias.
- Added programmatic profile metadata through `ProfileInfo`, `get_profile_info()` and `list_profile_info()` while preserving the stable four-function package-level API.
- Added opt-in diagnostics and strict validation with deterministic input classification (`mdc`, `unicode`, `mixed`, `ambiguous`, `none`), heuristic confidence and mixed-encoding warnings.
- Preserved multi-digit numeric runs in explicit MdC conversion while retaining `3` as the documented aleph alias in transliteration tokens.
- Made historical Egyptological yod normalization robust to additional and canonically reordered combining marks without discarding unrelated editorial diacritics.
- Added curated reference cases, exhaustive character/no-touch contracts and pinned Hypothesis property checks for idempotence, NFC output and Unicode normalization invariants.
- Recorded the Unicode 18.0 / UAX #57 revision 7 baseline used by the sign-code and transliteration contracts.
- Hardened wheel/sdist audits, reproducible wheel builds, public API contracts, deterministic Unicode fuzzing and cross-platform CI.
- Added isolated installed-artifact tests that verify packaged profile data, profile-aware conversion and CLI profile behavior from both wheel and source distribution.
- Added tag-gated PyPI Trusted Publishing through GitHub OIDC, plus a separate manual TestPyPI rehearsal workflow; no long-lived PyPI token is stored in the workflows.
- Added release-safety checks that enforce version-tag matching, OIDC scoping, protected publishing environments and immutable action SHA pins.
- Pinned GitHub Actions and the Python build/validation toolchain for reproducible release checks.

## 0.8.0

- Protected Gardiner, Hieroglyphica and JSesh sign identifiers from transliteration conversion using Unicode UAX #57 grammars.
- Tightened conservative automatic MdC detection to preserve ambiguous ASCII rather than guessing.
- Added exhaustive contracts for supported Egyptological Unicode, NFC/idempotence and Egyptian hieroglyph/format-control preservation.
- Expanded release validation across Python 3.10–3.14 plus Python-next testing.

## 0.7.0

- Added explicit `parse_mdc()` and `normalize_unicode()` workflows alongside conservative `parse()`.
- Added strict typing, wheel/sdist checks and synchronized release metadata validation.
