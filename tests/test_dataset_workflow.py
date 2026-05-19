from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from tdt.datasets.registry import load_config
from tdt.datasets.split import split_dataset
from tdt.preprocessing.tile_dataset import tile_dataset


def _write_test_dataset(tmp_path: Path):
    root = tmp_path / "dataset"
    images = root / "images"
    masks = root / "masks"
    images.mkdir(parents=True)
    masks.mkdir(parents=True)

    image = np.zeros((8, 8, 3), dtype=np.uint8)
    image[:, :, 0] = 80
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[1:6, 2:4] = 1
    mask[4:7, 5:7] = 2
    Image.fromarray(image).save(images / "sample_001.png")
    Image.fromarray(mask).save(masks / "sample_001.png")

    config_path = tmp_path / "dataset.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "name": "test_dataset",
                "task": "semantic_segmentation",
                "paths": {
                    "images": str(images),
                    "masks": str(masks),
                },
                "annotation": {"format": "mask", "background_id": 0},
                "classes": [
                    {
                        "id": 0,
                        "name": "background",
                        "morphology": "background",
                        "color": [0, 0, 0],
                    },
                    {
                        "id": 1,
                        "name": "crack",
                        "morphology": "linear",
                        "color": [255, 0, 0],
                    },
                    {
                        "id": 2,
                        "name": "leakage",
                        "morphology": "areal",
                        "color": [0, 0, 255],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return load_config(config_path)


def test_split_dataset_writes_split_files(tmp_path: Path):
    config = _write_test_dataset(tmp_path)

    split_csv = split_dataset(config, tmp_path / "splits", train=0.6, val=0.2)

    assert split_csv.exists()
    assert (tmp_path / "splits" / "splits.csv").exists()


def test_tile_dataset_writes_manifest_and_tiles(tmp_path: Path):
    config = _write_test_dataset(tmp_path)

    manifest = tile_dataset(
        config,
        tmp_path / "tiles",
        tile_size=(4, 4),
        stride=(4, 4),
        show_progress=False,
    )

    assert manifest.exists()
    assert len(list((tmp_path / "tiles" / "images" / "unsplit").glob("*.png"))) == 4
    assert len(list((tmp_path / "tiles" / "masks" / "unsplit").glob("*.png"))) == 4


def test_tile_dataset_uses_split_file(tmp_path: Path):
    config = _write_test_dataset(tmp_path)
    split_csv = split_dataset(config, tmp_path / "splits", train=0.6, val=0.2)

    manifest = tile_dataset(
        config,
        tmp_path / "split_tiles",
        tile_size=(4, 4),
        stride=(4, 4),
        splits_csv=split_csv,
        require_splits=True,
        show_progress=False,
    )

    assert manifest.exists()
    assert any((tmp_path / "split_tiles" / "images").glob("*/*.png"))
