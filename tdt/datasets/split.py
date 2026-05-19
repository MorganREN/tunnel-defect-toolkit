"""Source-image-level dataset splitting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random

import pandas as pd

from tdt.datasets.manifest import DatasetItem, collect_dataset_items
from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images

SPLIT_SCHEMA_VERSION = "tdt-splits-v1"


@dataclass(frozen=True)
class SplitRecord:
    """A source image split assignment."""

    image_id: str
    image_path: Path
    split: str


def split_source_images(
    image_dir: str | Path,
    train: float = 0.7,
    val: float = 0.15,
    seed: int = 42,
) -> list[SplitRecord]:
    """Split source images before patch generation to prevent tile leakage."""

    if not 0 < train < 1 or not 0 <= val < 1 or train + val >= 1:
        raise ValueError("Expected train and val fractions with train + val < 1.")

    images = list_images(image_dir)
    rng = Random(seed)
    rng.shuffle(images)

    n_total = len(images)
    n_train = int(round(n_total * train))
    n_val = int(round(n_total * val))

    records: list[SplitRecord] = []
    for index, image in enumerate(images):
        split = "train" if index < n_train else "val" if index < n_train + n_val else "test"
        records.append(SplitRecord(image_id=image.stem, image_path=image, split=split))
    return records


def split_dataset(
    config: DatasetConfig,
    output_dir: str | Path,
    train: float = 0.7,
    val: float = 0.15,
    seed: int = 42,
    require_masks: bool = True,
) -> Path:
    """Create source-image-level split files for a configured dataset."""

    if not 0 < train < 1 or not 0 <= val < 1 or train + val >= 1:
        raise ValueError("Expected train and val fractions with train + val < 1.")

    items = collect_dataset_items(config, require_masks=require_masks)
    rng = Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)

    n_total = len(shuffled)
    n_train = int(round(n_total * train))
    n_val = int(round(n_total * val))
    assigned: list[DatasetItem] = []
    for index, item in enumerate(shuffled):
        split = "train" if index < n_train else "val" if index < n_train + n_val else "test"
        assigned.append(
            DatasetItem(
                image_id=item.image_id,
                image_path=item.image_path,
                mask_path=item.mask_path,
                split=split,
            )
        )

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "schema_version": SPLIT_SCHEMA_VERSION,
            "image_id": item.image_id,
            "image_path": str(item.image_path),
            "mask_path": str(item.mask_path) if item.mask_path is not None else "",
            "split": item.split,
        }
        for item in sorted(assigned, key=lambda value: value.image_id)
    ]
    frame = pd.DataFrame(rows)
    split_csv = out / "splits.csv"
    frame.to_csv(split_csv, index=False)
    for split_name, group in frame.groupby("split"):
        (out / f"{split_name}.txt").write_text(
            "\n".join(group["image_id"].astype(str).tolist()) + "\n",
            encoding="utf-8",
        )
    return split_csv
