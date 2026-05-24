# example_data

`example_data` is the official small example dataset for
`tunnel-defect-toolkit`. It contains 20 real tunnel defect images selected from
an annotated collection maintained for this project, with paired LabelMe JSON
annotations and semantic masks generated from those annotations.

The data files in this directory are distributed under
[CC BY 4.0](DATA_LICENSE.md), separately from the toolkit source license.

The subset is selected to cover:

- all six foreground labels used in the source annotations
- single-class and multi-class images
- rare leakage subclasses (`leakageG`, `leakageW`)
- segment damage and lining falling off cases
- compact, medium, and high-resolution images

## Layout

```text
examples/example_data/
  images/              # source images
  annotations/         # LabelMe JSON annotations
  masks/               # semantic masks generated from annotations
  selection_manifest.csv
```

The public dataset config is:

```text
configs/example_data.yaml
```

## Usage

```bash
tdt validate configs/example_data.yaml
tdt analyze configs/example_data.yaml --out reports/example_data
tdt analyze configs/example_data.yaml --out reports/example_data_morphology --with-morphology --workers 2
tdt overlay configs/example_data.yaml --out reports/example_data_overlays --limit 20
```

For tiling, create source-image-level splits first:

```bash
tdt split configs/example_data.yaml --out reports/example_data_splits --seed 42
tdt tile configs/example_data.yaml \
  --out reports/example_data_tiles \
  --tile-size 512x512 \
  --stride 512x512 \
  --splits reports/example_data_splits/splits.csv \
  --require-splits
```

## Notes

The sample is intended for tutorial, documentation, and smoke-test workflows. It
is intentionally small and should not be treated as a statistically
representative release of the full source dataset.
