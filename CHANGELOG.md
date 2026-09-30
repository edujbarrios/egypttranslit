# Changelog

This file records user-visible changes. Citation metadata remains in `CITATION.cff`.

## 1.1.0

- Changed the default `parse()` and `parse_mdc()` presentation to IFAO-style plain-text transliteration, rendering aleph/ayin/yod as `ȝ`, `ʿ` and `ỉ` instead of the visually raised `ꜣ`, `ꜥ` and `ꞽ` forms.
- Added an explicit `ifao` output profile; `default` is now an alias of this profile.
- Added `unicode-canonical` for callers that need the previous 1.0.x `ꜣ/ꜥ/ꞽ` MdC output without changing plain `j` or `q`.
- Kept `normalize_unicode()` intentionally canonical: IFAO-style `ȝ ʿ ỉ` still normalizes to `ꜣ ꜥ ꞽ` when canonical Unicode is explicitly requested.
- Added regression coverage for IFAO plain-text samples and updated the CLI/documentation examples accordingly.

## 1.0.1

- Fixed profiled batch conversion so unknown profiles are rejected even when the input iterable is empty.
- Fixed diagnostics for uppercase Egyptological `ẖ` encoded as `H` plus COMBINING MACRON BELOW, which is now recognized as Unicode rather than ambiguous ASCII.
- Hardened the command-line interface so OS-level stdin/stdout failures return a concise I/O error instead of a traceback while preserving clean broken-pipe termination.

## 1.0.0

- First stable release.
- Added conservative automatic parsing, explicit MdC conversion and canonical Unicode normalization.
- Added declarative transliteration profiles, including `gardiner-1957` and the compatibility alias `legacy-diacritics`.
- Added batch conversion helpers for multiple transliterations while preserving input order.
- Added diagnostics and validation for ambiguous and mixed encodings.
- Added the `egypttranslit` CLI with `auto`, `mdc` and `unicode` modes.
- Protected Gardiner/JSesh sign identifiers and encoded hieroglyph data from accidental transliteration conversion.
- Added cross-platform tests, property checks, package validation and Trusted Publishing release workflows.

## 0.9.0

- Added the dependency-free `egypttranslit` command with `auto`, `mdc` and `unicode` modes, stdin support, explicit profile selection and deterministic UTF-8 I/O across Linux, macOS and Windows.
- Added declarative transliteration profiles backed by package data, including the explicit `gardiner-1957` convention (`j → ꞽ`, `q → ḳ`) and the backward-compatible `legacy-diacritics` alias.
- Added programmatic profile metadata through `ProfileInfo`, `get_profile_info()` and `list_profile_info()` while preserving the stable four-function package-level API.
- Added advanced batch helpers for automatic parsing, explicit MdC conversion, profile-aware MdC conversion and Unicode normalization; batch inputs preserve order and may be lists, tuples or generators.
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
