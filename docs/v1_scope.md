# V1 (`0.1.0`) Scope

`tunnel-defect-toolkit` V1 is a semantic-mask morphology analysis toolkit for
tunnel defect datasets.

## Included

- Dataset configuration, validation, and input diagnostics
- LabelMe to semantic-mask conversion and COCO-style polygon export
- Source image/mask manifests and deterministic source-image splitting
- Split-aware paired image/mask tiling
- Class, resolution, co-occurrence, mask-quality, and connected-region
  morphology analysis
- Morphology figures, mask overlay export, dataset reports, and dataset cards
- `analysis_metadata.json` provenance records for analysis runs
- A licensed repository-only `example_data` dataset for documentation and
  smoke tests; it is intentionally excluded from PyPI distributions

## Output Contract

- Morphology areas and lengths are reported in pixel units in V1.
- Same-class regions touching under the configured connectivity are one
  connected region.
- `analysis.morphology.connectivity` defaults to `2`; accepted values are `1`
  and `2`.
- `analysis.morphology.min_area_px` defaults to `1`; excluded smaller regions
  are not represented in morphology tables.

V1 public interfaces operate on dataset assets, semantic masks, annotations,
derived tables, paired tiles, and descriptive reports only.

## Versioning Policy

Artifact schemas are stable within the `0.1.x` line. Any change that removes or
renames an output column requires a minor-version release and a changelog entry.
