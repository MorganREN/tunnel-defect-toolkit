"""Mask processing helpers."""

from __future__ import annotations

import numpy as np


def binary_mask(mask: np.ndarray, class_id: int) -> np.ndarray:
    """Return a boolean mask for one semantic class."""

    return np.asarray(mask) == class_id


def foreground_mask(mask: np.ndarray, background_id: int = 0, ignore_index: int | None = 255) -> np.ndarray:
    """Return a boolean foreground mask."""

    arr = np.asarray(mask)
    out = arr != background_id
    if ignore_index is not None:
        out &= arr != ignore_index
    return out


def class_ids_present(mask: np.ndarray, ignore_index: int | None = 255) -> set[int]:
    """Return class ids present in a semantic mask."""

    values = set(int(v) for v in np.unique(mask))
    if ignore_index is not None:
        values.discard(int(ignore_index))
    return values
