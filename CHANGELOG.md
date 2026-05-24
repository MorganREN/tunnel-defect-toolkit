# Changelog

## 0.1.0 - 2026-05-24

Initial V1 release candidate.

### Added

- `tdt` CLI for configuration validation, annotation conversion, manifests,
  splitting, analysis, visualization, and paired tiling.
- YAML dataset schema with configurable morphology policy.
- LabelMe-to-mask and LabelMe-to-COCO conversion with input diagnostics.
- Class distribution, resolution summaries, co-occurrence matrices, quality
  summaries, and connected-region morphology profiling.
- Pixel-unit morphology descriptor schema and `analysis_metadata.json`
  provenance record.
- Morphology plots, annotation overlay export, dataset cards, and HTML reports.
- A repository-only `example_data` directory, containing a 20-image CC BY 4.0
  example dataset with LabelMe annotations, derived semantic masks, and
  selection metadata.
- CI, packaging checks, MIT software license, data license, and citation
  metadata.

### Changed

- V1 distribution is limited to semantic-mask dataset characterisation,
  reporting, visualization, conversion, splitting, and paired tiling.
