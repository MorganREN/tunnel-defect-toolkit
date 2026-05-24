"""Class co-occurrence analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images, read_mask


def cooccurrence_matrix(config: DatasetConfig) -> pd.DataFrame:
    """Compute image-level class co-occurrence counts."""

    if config.paths.masks is None:
        raise ValueError("cooccurrence_matrix requires config.paths.masks.")

    class_ids = [item.id for item in config.classes]
    matrix: np.ndarray = np.zeros((len(class_ids), len(class_ids)), dtype=np.int64)
    for mask_path in list_images(config.paths.masks):
        present = set(int(v) for v in np.unique(read_mask(mask_path)))
        for i, class_i in enumerate(class_ids):
            for j, class_j in enumerate(class_ids):
                matrix[i, j] += int(class_i in present and class_j in present)
    names = [item.name for item in config.classes]
    return pd.DataFrame(matrix, index=names, columns=names)
