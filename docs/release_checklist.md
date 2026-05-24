# Release Checklist

## One-Time Repository Setup

1. Configure the `testpypi` and `pypi` GitHub Environments, preferably with a
   required reviewer.
2. Register Trusted Publishers for repository
   `MorganREN/tunnel-defect-toolkit`:
   - TestPyPI workflow: `.github/workflows/testpypi.yml`, environment `testpypi`
   - PyPI workflow: `.github/workflows/release.yml`, environment `pypi`
3. Confirm the package name `tunnel-defect-toolkit` is available or already
   owned by the maintainer on each index.

## Release Candidate Verification

Update `tdt.__version__`, `pyproject.toml`, `CITATION.cff`, and `CHANGELOG.md`,
then run:

```bash
python -m pip install -e ".[dev]" build twine
ruff check .
mypy tdt
pytest
python -m build
python -m twine check dist/*
python tests/check_distribution.py dist/*
```

Verify the official repository example:

```bash
tdt validate configs/example_data.yaml
tdt analyze configs/example_data.yaml \
  --out reports/release_morphology \
  --with-morphology \
  --workers 1
tdt plot-morphology reports/release_morphology/morphology_descriptors.csv \
  --out reports/release_morphology/figures
tdt split configs/example_data.yaml --out reports/release_splits --seed 42
tdt tile configs/example_data.yaml \
  --out reports/release_tiles \
  --tile-size 512x512 \
  --stride 512x512 \
  --splits reports/release_splits/splits.csv \
  --require-splits
```

Confirm the repository-only `example_data` assets are not present in the wheel
or source distribution; they have a separate data license from the PyPI
distribution.

## Publication Sequence

1. Run the `Publish to TestPyPI` workflow manually.
2. Install the uploaded TestPyPI artifact in a clean environment and repeat a
   CLI smoke test using local data.
3. Create and publish a GitHub Release for the verified tag.
4. The `Publish to PyPI` workflow publishes that release through Trusted
   Publishing without stored package-index tokens.

The workflow follows the PyPI Trusted Publishing guidance:
<https://docs.pypi.org/trusted-publishers/using-a-publisher/>.
