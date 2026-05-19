"""Source-image-level dataset splitting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import Random

from tdt.utils.io import list_images


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
