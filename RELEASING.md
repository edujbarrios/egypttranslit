# Releasing egypttranslit

This checklist prepares a release without publishing anything automatically.

## 1. Start from a green `main`

GitHub Actions must pass:

- Python 3.10, 3.11, 3.12, 3.13 and 3.14 tests on Linux;
- the full suite on current GitHub-hosted Windows and macOS runners;
- compile, lint, formatting and strict type checks;
- release metadata synchronization;
- wheel and source-distribution builds;
- `twine check`;
- the wheel reproducibility check with a fixed `SOURCE_DATE_EPOCH`;
- the artifact-content audit;
- isolated installation from both wheel and sdist.

The Python 3.15 pre-release job is informative and is allowed to fail until 3.15 becomes a supported release.

## 2. Set the release version

Update the version in exactly these release metadata files:

- `pyproject.toml`;
- `CITATION.cff`.

`egypttranslit.__version__` is read from the installed distribution metadata and must not be edited manually.

The build backend in `pyproject.toml` is intentionally pinned with `==`. Updating setuptools is a reviewed maintenance change: change the pin explicitly and let the complete CI gate rebuild and revalidate the distributions.

Then run:

```bash
python -m pip install -e .
python scripts/check_release.py
python -m unittest discover -s tests
```

## 3. Build clean artifacts

The CI release toolchain is pinned to:

- `setuptools==84.0.0` as the PEP 517 build backend;
- `build==1.6.1`;
- `twine==7.0.0`;
- `mypy==2.3.1` and `ruff==0.16.9` for quality checks.

For a local release check, use the same packaging tools:

```bash
rm -rf build dist *.egg-info
python -m pip install build==1.6.1 twine==7.0.0
export SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"
python -m build
python -m twine check dist/*
python scripts/check_artifacts.py
```

Both a wheel and a source distribution must be produced. `SOURCE_DATE_EPOCH` gives the wheel a deterministic timestamp input; CI independently builds the wheel twice with the same epoch and requires byte-for-byte equality. This repository does not claim that the setuptools sdist is bit-for-bit reproducible.

## 4. Inspect the artifacts

Confirm that the wheel contains only the runtime package and distribution metadata, including `py.typed`, `LICENSE` and `NOTICE`. The source distribution must also contain the README, citation metadata, release documentation, tests and release-audit scripts. Neither artifact may contain caches, bytecode, repository metadata, environment files, private-key-like files or unsafe archive paths.

CI performs these checks automatically, but they should still be reviewed before the first public release.

## 5. Publishing policy

Do not store a long-lived PyPI API token in this repository.

For the eventual PyPI release, prefer PyPI Trusted Publishing with a dedicated GitHub Actions workflow and a protected `pypi` environment. PyPI recommends Trusted Publishing because GitHub can authenticate with short-lived OIDC credentials instead of a stored API token.

No publishing workflow is intentionally included yet. Creating or enabling one is a separate release action.

Official references:

- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/
- PyPI GitHub Actions publisher: https://docs.pypi.org/trusted-publishers/using-a-publisher/
- Python Packaging User Guide: https://packaging.python.org/en/latest/flow/
- Reproducible Builds, `SOURCE_DATE_EPOCH`: https://reproducible-builds.org/docs/source-date-epoch/
