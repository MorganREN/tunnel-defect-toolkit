"""Resolution distribution analysis."""

from __future__ import annotations

import pandas as pd
from PIL import Image

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images
from tdt.utils.progress import progress


def resolution_table(config: DatasetConfig, show_progress: bool = True) -> pd.DataFrame:
    """Return per-image resolution metadata."""

    rows = []
    image_paths = list_images(config.paths.images)
    for image_path in progress(
        image_paths,
        total=len(image_paths),
        desc="Resolution analysis",
        enabled=show_progress,
    ):
        with Image.open(image_path) as image:
            width, height = image.size
        rows.append(
            {
                "image_id": image_path.stem,
                "path": str(image_path),
                "width": width,
                "height": height,
                "megapixels": width * height / 1_000_000,
                "aspect_ratio": width / height if height else 0,
                "resolution_group": resolution_group(width, height),
            }
        )
    return pd.DataFrame(rows)


def resolution_group(width: int, height: int) -> str:
    """Assign a simple resolution group based on megapixels."""

    megapixels = width * height / 1_000_000
    if megapixels < 0.5:
        return "small"
    if megapixels < 2.0:
        return "medium"
    if megapixels < 8.0:
        return "large"
    return "ultra"
