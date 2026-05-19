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
name: my_tunnel_dataset
task: semantic_segmentation

paths:
  images: data/raw/my_dataset/images
  annotations: data/raw/my_dataset/annotations
  masks: data/raw/my_dataset/masks
  splits: data/raw/my_dataset/splits

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

`example_data` is the official small real dataset shipped with the repository:

```bash
tdt validate configs/example_data.yaml
tdt analyze configs/example_data.yaml --out reports/example_data
tdt split configs/example_data.yaml --out reports/example_data_splits
tdt tile configs/example_data.yaml --out reports/example_data_tiles --tile-size 512x512 --stride 512x512
```

For a private LabelMe dataset, copy `configs/labelme_template.yaml` to a local
config file, edit its paths and classes, then run:

```bash
tdt validate configs/local_my_dataset.yaml
tdt labelme-to-masks configs/local_my_dataset.yaml
tdt manifest configs/local_my_dataset.yaml --out data/raw/my_dataset/manifest.csv
tdt split configs/local_my_dataset.yaml --out data/raw/my_dataset/splits
tdt analyze configs/local_my_dataset.yaml --out data/raw/my_dataset/analysis_output
tdt tile configs/local_my_dataset.yaml --out data/processed/my_dataset_tiles
tdt overlay configs/local_my_dataset.yaml --out data/raw/my_dataset/overlays --limit 24
```

## Full Morphology Profiling

Full morphology profiling computes connected-instance descriptors including
compactness, elongation, solidity, skeleton length, and medial-axis width. It can
be slow on high-resolution masks, so workers are explicitly controlled:

```bash
tdt analyze configs/example_data.yaml \
  --out reports/example_data_morphology \
  --with-morphology \
  --workers 2
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
