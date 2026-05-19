# CLI Reference

## `tdt validate`

Validate dataset config paths, classes, and image/mask pairing.

```bash
tdt validate configs/toy.yaml
```

## `tdt labelme-to-masks`

Convert LabelMe polygon annotations to semantic masks.

```bash
tdt labelme-to-masks configs/tongji_flat.yaml
```

## `tdt labelme-to-coco`

Convert LabelMe polygon annotations to a COCO-style JSON file.

```bash
tdt labelme-to-coco configs/tongji_flat.yaml --out annotations.coco.json
```

## `tdt manifest`

Write image/mask manifest.

```bash
tdt manifest configs/tongji_flat.yaml --out manifest.csv
```

## `tdt split`

Create source-image-level train/val/test splits.

```bash
tdt split configs/tongji_flat.yaml --out splits --train 0.7 --val 0.15 --seed 42
```

## `tdt analyze`

Generate dataset reports. Add `--with-morphology` for full instance-level shape
descriptors.

```bash
tdt analyze configs/tongji_flat.yaml --out analysis_output
tdt analyze configs/tongji_flat.yaml --out analysis_output_morphology --with-morphology --workers 4
```

## `tdt tile`

Generate image/mask tiles. If a split file is available, output tiles are
separated into split subdirectories and the split is recorded in
`tile_manifest.csv`.

```bash
tdt tile configs/tongji_flat.yaml --out tiles --require-splits
```

## `tdt overlay`

Export image/mask overlay figures.

```bash
tdt overlay configs/tongji_flat.yaml --out overlays --limit 24
```

## `tdt plot-morphology`

Generate morphology figures from `morphology_descriptors.csv`.

```bash
tdt plot-morphology morphology_descriptors.csv --out figures --formats png,pdf
```
