# Changelog

## 0.1.0 - 2026-05-19

Initial alpha release candidate.

### Added

- Model-agnostic package scaffold with `tdt` CLI.
- Dataset YAML schema and validation.
- LabelMe-to-mask and LabelMe-to-COCO conversion.
- Source image/mask manifest generation.
- Source-image-level splitting.
- Split-aware resolution-adaptive tiling and tile manifests.
- Dataset analysis reports, dataset cards, class distribution, resolution summaries,
  co-occurrence matrices, quality summaries, and morphology profiling.
- Morphology plots and mask overlay export.
- `example_data`, a 20-image real tunnel defect example dataset with LabelMe
  annotations, generated semantic masks, and selection metadata.
- Tests, CI workflow, MIT license, and citation metadata.

### Not Included

- Model training framework.
- Benchmark evaluation pipeline for prediction folders.
- Model architecture, routing visualization, or quantization helpers.
