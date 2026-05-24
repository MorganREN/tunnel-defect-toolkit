# Tunnel Defect Toolkit

`tunnel-defect-toolkit` (`tdt`) is a Python toolkit for reproducible
characterisation of semantic-mask tunnel defect datasets. It converts polygon
annotations, audits dataset quality, computes connected-region morphology,
creates paired tiles, and exports figures and reports suitable for research
records.

## V1 (`0.1.0`) Capability Boundary

V1 provides:

- YAML dataset configuration and input validation
- LabelMe polygon conversion to semantic masks and COCO-style polygon JSON
- Image/mask manifests and deterministic source-image splits
- Class distribution, resolution, co-occurrence, and mask-quality analysis
- Connected-region morphology descriptors in pixel units
- Morphology figures, annotation overlays, dataset cards, and HTML reports
- Resolution-adaptive paired image/mask tiling

V1 is limited to dataset assets and annotations. Its stable outputs are the
manifests, tables, figures, reports, and paired tiles documented under
[`docs/`](docs/index.md).

## Installation

Install the lightweight package from PyPI:

```bash
pip install tunnel-defect-toolkit
```

For the official example data, documentation, and development checks, clone the
repository:

```bash
git clone https://github.com/MorganREN/tunnel-defect-toolkit.git
cd tunnel-defect-toolkit
pip install -e ".[dev]"
```

The PyPI wheel and source distribution contain the MIT-licensed library, CLI,
documentation, and configuration template. The licensed `example_data` tutorial
assets are available in the GitHub repository only, keeping PyPI distribution
licensing unambiguous.

## Official Example Workflow

The GitHub repository directory `examples/example_data/` contains 20 annotated
tunnel-defect images distributed under `CC BY 4.0`; see its
[`DATA_LICENSE.md`](https://github.com/MorganREN/tunnel-defect-toolkit/blob/main/examples/example_data/DATA_LICENSE.md).

```bash
tdt validate configs/example_data.yaml
tdt analyze configs/example_data.yaml \
  --out reports/example_data_morphology \
  --with-morphology \
  --workers 2
tdt plot-morphology \
  reports/example_data_morphology/morphology_descriptors.csv \
  --out reports/example_data_morphology/figures \
  --formats png,pdf
tdt overlay configs/example_data.yaml --out reports/example_data_overlays --limit 20
tdt split configs/example_data.yaml --out reports/example_data_splits --seed 42
tdt tile configs/example_data.yaml \
  --out reports/example_data_tiles \
  --tile-size 512x512 \
  --stride 512x512 \
  --splits reports/example_data_splits/splits.csv \
  --require-splits
```

`tdt analyze --with-morphology` writes descriptor columns with explicit pixel
units and an `analysis_metadata.json` record of class mapping, input-manifest
digest, analysis policy, package version, and run time. V1 treats touching
regions of the same class as one connected region according to the configured
connectivity.

## Run On Your Data

Place a local LabelMe dataset under `data/raw/` and start from the template:

```bash
cp configs/labelme_template.yaml configs/local_my_dataset.yaml
```

Edit paths and label mappings, then run:

```bash
tdt validate configs/local_my_dataset.yaml
tdt labelme-to-masks configs/local_my_dataset.yaml
tdt manifest configs/local_my_dataset.yaml --out data/raw/my_dataset/manifest.csv
tdt split configs/local_my_dataset.yaml --out data/raw/my_dataset/splits --seed 42
tdt analyze configs/local_my_dataset.yaml \
  --out data/raw/my_dataset/analysis_output \
  --with-morphology \
  --workers auto
tdt overlay configs/local_my_dataset.yaml --out data/raw/my_dataset/overlays --limit 24
tdt tile configs/local_my_dataset.yaml --out data/processed/my_dataset_tiles
```

Shape-analysis policy can be placed in the YAML config:

```yaml
analysis:
  ignore_index: 255
  min_foreground_px: 4
  morphology:
    connectivity: 2
    min_area_px: 1
```

The command line can override region policy for a recorded analysis run:

```bash
tdt analyze configs/local_my_dataset.yaml \
  --out data/raw/my_dataset/analysis_filtered \
  --with-morphology \
  --connectivity 2 \
  --min-area-px 16
```

Keep datasets out of version control unless their license permits
redistribution.

## Package And Citation

- PyPI package: `tunnel-defect-toolkit`
- Python import and CLI: `tdt`
- Repository: [MorganREN/tunnel-defect-toolkit](https://github.com/MorganREN/tunnel-defect-toolkit)

Use [`CITATION.cff`](CITATION.cff) when citing the software. The source code is
licensed under MIT; the included example dataset has its separate CC BY 4.0
license.
