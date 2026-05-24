"""Class distribution analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images, read_mask
from tdt.utils.progress import progress


def class_distribution(config: DatasetConfig, show_progress: bool = True) -> pd.DataFrame:
    """Compute image, pixel, and instance-presence statistics per class."""

    if config.paths.masks is None:
        raise ValueError("class_distribution requires config.paths.masks.")

    mask_paths = list_images(config.paths.masks)
    image_counts = {item.id: 0 for item in config.classes}
    pixel_counts = {item.id: 0 for item in config.classes}
    class_ids = sorted(pixel_counts)
    total_pixels = 0
    for mask_path in progress(
        mask_paths,
        total=len(mask_paths),
        desc="Class distribution",
        enabled=show_progress,
    ):
        mask = read_mask(mask_path)
        total_pixels += int(mask.size)
        values, counts = np.unique(mask, return_counts=True)
        counts_by_id = dict(zip((int(value) for value in values), (int(count) for count in counts)))
        for class_id in class_ids:
            pixels = counts_by_id.get(class_id, 0)
            pixel_counts[class_id] += pixels
            image_counts[class_id] += int(pixels > 0)

    rows = [
        {
            "class_id": item.id,
            "class_name": item.name,
            "morphology": item.morphology,
            "image_count": image_counts[item.id],
            "pixel_count": pixel_counts[item.id],
        }
        for item in config.classes
    ]
    frame = pd.DataFrame(rows)
    annotated_pixels = max(
        int(frame.loc[frame["class_id"] != config.background_id, "pixel_count"].sum()), 1
    )
    frame["pixel_share"] = frame["pixel_count"] / total_pixels
    frame["foreground_pixel_share"] = frame.apply(
        lambda row: 0.0
        if row["class_id"] == config.background_id
        else row["pixel_count"] / annotated_pixels,
        axis=1,
    )
    return frame


def mask_class_distribution(
    mask_paths: list[str | Path],
    class_ids: list[int],
    show_progress: bool = True,
) -> pd.DataFrame:
    """Compute pixel counts for a list of masks."""

    rows = []
    for class_id in class_ids:
        count = 0
        for path in progress(
            mask_paths,
            total=len(mask_paths),
            desc=f"Class {class_id} pixels",
            enabled=show_progress,
        ):
            count += int((read_mask(path) == class_id).sum())
        rows.append({"class_id": class_id, "pixel_count": count})
    return pd.DataFrame(rows)
