# Tunnel Defect Toolkit

`tunnel-defect-toolkit` is a model-agnostic Python toolkit for tunnel defect
dataset analysis, resolution-adaptive preprocessing, visualization, and
reproducible reporting.

The package is designed to support morphology-aware tunnel defect benchmark and
dataset papers first, while keeping a clean bridge to later TMDS model releases.

## Scope of V1.0.0

V1.0.0 focuses on dataset and preprocessing utilities:

- Dataset schemas and configuration validation
- LabelMe / mask-oriented dataset conversion hooks
- Morphology profiling for linear and areal defects
- Class, pixel, instance, and resolution distribution analysis
- Source-image-level splitting to avoid patch leakage
- Resolution-adaptive tiling and Gaussian-weighted stitching
- Split-aware tile generation
- Static dataset and evaluation reports
- CLI entry points

V1 intentionally does not include TMDS model code, routing visualization, model
training framework bindings, quantization tooling, or a benchmark evaluation
pipeline.

## Installation

Install the package from PyPI:

```bash
pip install tunnel-defect-toolkit
```

For development, tests, and repository examples:

```bash
git clone https://github.com/MorganREN/tunnel-defect-toolkit.git
cd tunnel-defect-toolkit
pip install -e ".[dev]"
```

## Quick Start

The following toy commands assume you are working from a cloned repository,
because the toy data and example configs live in the GitHub repo rather than in
the installed wheel.

Validate the toy dataset config:

```bash
tdt validate configs/toy.yaml
```

Generate a dataset report:

```bash
tdt analyze configs/toy.yaml --out reports/toy_dataset
```

Create source-level splits and tiles for the toy dataset:

```bash
tdt split configs/toy.yaml --out reports/toy_splits --seed 42
tdt tile configs/toy.yaml \
  --out reports/toy_tiles \
  --tile-size 4x4 \
  --stride 4x4 \
  --splits reports/toy_splits/splits.csv \
  --require-splits
```

For your own LabelMe dataset, copy the template and edit the paths/classes:

```bash
cp configs/labelme_template.yaml configs/local_my_dataset.yaml
```

Then run the dataset workflow with your local config:

```bash
# 1. Convert LabelMe polygons to semantic masks
tdt labelme-to-masks configs/local_my_dataset.yaml

# 2. Write a source image/mask manifest
tdt manifest configs/local_my_dataset.yaml --out data/raw/my_dataset/manifest.csv

# 3. Create source-image-level splits before tiling
tdt split configs/local_my_dataset.yaml --out data/raw/my_dataset/splits --seed 42

# 4. Generate dataset analysis reports
tdt analyze configs/local_my_dataset.yaml --out data/raw/my_dataset/analysis_output

# 5. Generate resolution-adaptive image/mask tiles
tdt tile configs/local_my_dataset.yaml --out data/processed/my_dataset_tiles

# 6. Export annotation overlays for visual QA
tdt overlay configs/local_my_dataset.yaml --out data/raw/my_dataset/overlays --limit 24
```

Run full morphology profiling with process workers:

```bash
tdt analyze configs/local_my_dataset.yaml \
  --out data/raw/my_dataset/analysis_output_morphology \
  --with-morphology \
  --workers 4
```

Use `--workers auto` for a conservative automatic process count. If process
workers are unavailable in a restricted environment, the toolkit falls back to
single-process execution with a warning.

Generate morphology figures from descriptor CSV:

```bash
tdt plot-morphology \
  data/raw/my_dataset/analysis_output_morphology/morphology_descriptors.csv \
  --out data/raw/my_dataset/analysis_output_morphology/figures \
  --formats png,pdf
```

Export COCO-style polygon annotations:

```bash
tdt labelme-to-coco configs/local_my_dataset.yaml --out data/raw/my_dataset/annotations.coco.json
```

## V1 Boundaries

V1.0.0 can:

- validate dataset configs
- convert LabelMe polygons to masks and COCO-style JSON
- write source manifests
- create source-image-level train/val/test splits
- generate split-aware image/mask tiles
- profile class, resolution, quality, co-occurrence, and morphology statistics
- export morphology figures and mask overlays
- write HTML reports and dataset cards

V1.0.0 does not:

- train models
- run benchmark evaluation on predictions
- include TMDS architecture, routing maps, or learned modules
- export ONNX/TensorRT/INT8 deployments
- provide an interactive web app

## Dataset Placement

The repository includes a tiny toy mask dataset under:

```text
examples/toy_dataset/
```

Place your own datasets manually under:

```text
data/raw/
```

Use `configs/labelme_template.yaml` as a starting point for private LabelMe
datasets. Local configs named `configs/local*.yaml` are ignored by git so that
dataset-specific paths and class mappings do not leak into the public package.

Keep real datasets out of version control unless their license explicitly allows
redistribution.

## Package Names

- PyPI package: `tunnel-defect-toolkit`
- Python import: `tdt`

## Citation

If you use this toolkit in academic work, cite the accompanying dataset or
benchmark paper once released. A provisional `CITATION.cff` is included.
