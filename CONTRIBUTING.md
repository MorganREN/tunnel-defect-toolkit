# Contributing

This project is currently an early-stage research toolkit. Contributions should
preserve the V1 boundary: dataset analysis, preprocessing, visualization, and
reporting utilities only. Model training, benchmark evaluation, TMDS-specific
modules, routing visualization, and quantization should be proposed for later
versions.

## Local Checks

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Data Policy

Do not commit restricted datasets, generated masks, generated reports, or local
inspection outputs. Place private or licensed datasets under `data/raw/`, which
is ignored by git except for `data/raw/README.md`.

## API Expectations

Public functions should include type hints and docstrings. CLI commands should
write explicit artifacts and print their output paths.
