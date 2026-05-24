# Contributing

Contributions to the `0.1.x` line must preserve the V1 public contract:
semantic-mask dataset conversion, validation, morphology analysis,
visualization, reporting, splitting, and paired tiling.

## Local Checks

```bash
pip install -e ".[dev]"
ruff check .
mypy tdt
pytest
python -m build
python -m twine check dist/*
```

## Data Policy

Do not commit data unless redistribution rights and a data-specific license are
documented. Place private or restricted datasets under `data/raw/`, which is
ignored by git except for `data/raw/README.md`.

## API Expectations

Public functions must include type hints and docstrings. CLI commands must emit
explicit artifacts and clear input errors. Changes to output columns or schema
semantics require documentation, tests, and a changelog entry.
