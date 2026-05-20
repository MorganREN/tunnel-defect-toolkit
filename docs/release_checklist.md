# Release Checklist

Before publishing to PyPI:

1. Update `tdt.__version__`, `pyproject.toml`, and `CHANGELOG.md`.
2. Run:

```bash
ruff check .
pytest
python -m compileall -q tdt
python -m build
```

3. Inspect generated distributions under `dist/`.
4. Verify CLI smoke tests:

```bash
tdt --version
tdt validate configs/example_data.yaml
tdt analyze configs/example_data.yaml --out reports/release_check --with-morphology --workers 1
tdt split configs/example_data.yaml --out reports/release_splits --seed 42
tdt tile configs/example_data.yaml \
  --out reports/release_tiles \
  --tile-size 512x512 \
  --stride 512x512 \
  --splits reports/release_splits/splits.csv \
  --require-splits
```

5. Publish first to TestPyPI if credentials are available.
