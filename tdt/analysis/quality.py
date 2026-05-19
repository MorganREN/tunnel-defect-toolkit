"""Annotation quality checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images, read_mask
from tdt.utils.progress import progress


@dataclass(frozen=True)
class QualityIssue:
    """One annotation quality issue."""

    image_id: str
    issue: str
    detail: str


def check_mask_quality(
    config: DatasetConfig,
    min_foreground_pixels: int = 4,
    show_progress: bool = True,
) -> list[QualityIssue]:
    """Run lightweight quality checks on semantic masks."""

    if config.paths.masks is None:
        raise ValueError("check_mask_quality requires config.paths.masks.")

    issues: list[QualityIssue] = []
    valid_ids = config.class_ids
    mask_paths = list_images(config.paths.masks)
    for mask_path in progress(
        mask_paths,
        total=len(mask_paths),
        desc="Quality checks",
        enabled=show_progress,
    ):
        mask = read_mask(mask_path)
        values = set(int(v) for v in np.unique(mask))
        unknown = values - valid_ids
        if config.ignore_index is not None:
            unknown.discard(int(config.ignore_index))
        if unknown:
            issues.append(QualityIssue(mask_path.stem, "unknown_class_id", str(sorted(unknown))))

        foreground = mask != config.background_id
        if config.ignore_index is not None:
            foreground &= mask != config.ignore_index
        count = int(np.count_nonzero(foreground))
        if count == 0:
            issues.append(QualityIssue(mask_path.stem, "empty_foreground", "No foreground pixels."))
        elif count < min_foreground_pixels:
            issues.append(
                QualityIssue(mask_path.stem, "tiny_foreground", f"{count} foreground pixels.")
            )
    return issues
