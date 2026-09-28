# Releasing egypttranslit

This checklist prepares a release without publishing anything automatically.

## 1. Start from a green `main`

GitHub Actions must pass:

- Python 3.10, 3.11, 3.12, 3.13 and 3.14 tests;
- compile, lint, formatting and strict type checks;
- release metadata synchronization;
- wheel and source-distribution builds;
- `twine check`;
- isolated installation from both wheel and sdist.

The Python 3.15 pre-release job is informative and is allowed to fail until 3.15 becomes a supported release.

## 2. Set the release version

Update the version in exactly these release metadata files:

- `pyproject.toml`;
- `CITATION.cff`.

`egypttranslit.__version__` is read from the installed distribution metadata and must not be edited manually.

Then run:

```bash
python -m pip install -e .
python scripts/check_release.py
python -m unittest discover -s tests
```

## 3. Build clean artifacts

```bash
rm -rf build dist *.egg-info
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

Both a wheel and a source distribution must be produced.

## 4. Inspect the artifacts

Confirm that the wheel contains the package, `py.typed`, `LICENSE` and `NOTICE`, and that the source distribution also contains `README.md`, `CITATION.cff` and the tests.

CI performs these checks automatically, but they should still be reviewed before the first public release.

## 5. Publishing policy

Do not store a long-lived PyPI API token in this repository.

For the eventual PyPI release, prefer PyPI Trusted Publishing with a dedicated GitHub Actions workflow and a protected `pypi` environment. PyPI recommends Trusted Publishing because GitHub can authenticate with short-lived OIDC credentials instead of a stored API token.

No publishing workflow is intentionally included yet. Creating or enabling one is a separate release action.

Official references:

- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/
- PyPI GitHub Actions publisher: https://docs.pypi.org/trusted-publishers/using-a-publisher/
- Python Packaging User Guide: https://packaging.python.org/en/latest/flow/
