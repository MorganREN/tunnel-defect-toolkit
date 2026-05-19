# V1.0.0 Scope

`tunnel-defect-toolkit` V1.0.0 is a model-agnostic dataset and preprocessing
toolkit for tunnel defect segmentation datasets.

## Included

- Dataset configuration and validation
- LabelMe to semantic mask conversion
- LabelMe to COCO-style polygon export
- Source image/mask manifest generation
- Source-image-level train/val/test splitting
- Split-aware image/mask tiling
- Dataset profiling:
  - class distribution
  - resolution distribution
  - co-occurrence matrix
  - annotation quality checks
  - morphology descriptors
- Morphology figures
- Mask overlay export
- Dataset report and dataset card generation
- A small real `example_data` dataset for documentation and smoke-test workflows

## Excluded

- Model training
- Prediction-folder benchmark evaluation
- TMDS model code
- Routing map visualization
- Quantization and deployment export
- Interactive web dashboard
- Dataset hosting

## Versioning Policy

V1 artifact schemas are considered stable within the `0.1.x` line. New columns
may be added, but existing column names should not be removed without a minor
version bump.
