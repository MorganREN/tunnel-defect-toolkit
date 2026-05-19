# Tunnel Defect Toolkit Documentation

`tunnel-defect-toolkit` is organized around a reproducible dataset workflow:

```text
configure -> validate -> convert -> manifest -> split -> analyze -> tile -> visualize
```

The V1 release is intentionally model-agnostic. It does not include a training
framework and does not run benchmark evaluation by default.

## Dataset Configuration

Create one YAML file per dataset under `configs/`. A minimal semantic
segmentation config declares paths, annotation format, class ids, colors, and
morphology labels:

```yaml
name: tongji
task: semantic_segmentation

paths:
  images: data/raw/tongji
  annotations: data/raw/tongji
  masks: data/raw/tongji/masks
  splits: data/raw/tongji/splits

annotation:
  format: labelme
  background_id: 0

classes:
  - id: 0
    name: background
    morphology: background
    color: [0, 0, 0]
  - id: 1
    name: crack
    aliases: [crack]
    morphology: linear
    color: [255, 0, 0]
```

## CLI Workflow

```bash
tdt validate configs/tongji_flat.yaml
tdt labelme-to-masks configs/tongji_flat.yaml
tdt manifest configs/tongji_flat.yaml --out data/raw/tongji/manifest.csv
tdt split configs/tongji_flat.yaml --out data/raw/tongji/splits
tdt analyze configs/tongji_flat.yaml --out data/raw/tongji/analysis_output
tdt tile configs/tongji_flat.yaml --out data/processed/tongji_tiles
tdt overlay configs/tongji_flat.yaml --out data/raw/tongji/overlays --limit 24
```

## Full Morphology Profiling

Full morphology profiling computes connected-instance descriptors including
compactness, elongation, solidity, skeleton length, and medial-axis width. It can
be slow on high-resolution masks, so workers are explicitly controlled:

```bash
tdt analyze configs/tongji_flat.yaml \
  --out data/raw/tongji/analysis_output_morphology \
  --with-morphology \
  --workers 4
```

## Generated Artifacts

`tdt analyze` writes:

- `dataset_report.html`
- `dataset_card.md`
- `class_distribution.csv`
- `resolution_table.csv`
- `resolution_summary.csv`
- `cooccurrence_matrix.csv`
- `quality_issues.csv`
- `quality_summary.csv`
- `morphology_descriptors.csv` when `--with-morphology` is enabled
- `morphology_summary.csv` when `--with-morphology` is enabled

`tdt tile` writes:

- `images/*.png`
- `masks/*.png`
- `tile_manifest.csv`

## Additional Documentation

- [V1 scope](v1_scope.md)
- [CLI reference](cli_reference.md)
- [Artifact schema](artifact_schema.md)
- [Release checklist](release_checklist.md)
