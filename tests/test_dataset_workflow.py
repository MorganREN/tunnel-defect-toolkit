from pathlib import Path

from tdt.datasets.registry import load_config
from tdt.datasets.split import split_dataset
from tdt.preprocessing.tile_dataset import tile_dataset


def test_split_dataset_writes_split_files(tmp_path: Path):
    config = load_config("configs/toy.yaml")

    split_csv = split_dataset(config, tmp_path / "splits", train=0.6, val=0.2)

    assert split_csv.exists()
    assert (tmp_path / "splits" / "splits.csv").exists()


def test_tile_dataset_writes_manifest_and_tiles(tmp_path: Path):
    config = load_config("configs/toy.yaml")

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
    config = load_config("configs/toy.yaml")
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
