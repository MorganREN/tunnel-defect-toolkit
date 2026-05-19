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
tdt validate configs/toy.yaml
tdt analyze configs/toy.yaml --out reports/release_check --with-morphology --workers 1
tdt tile configs/toy.yaml --out reports/release_tiles --tile-size 4x4 --stride 4x4
```

5. Publish first to TestPyPI if credentials are available.
