"""Structure-aware segmentation metrics."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation
from skimage.measure import label
from skimage.morphology import skeletonize
from skimage.segmentation import find_boundaries


def boundary_f1(y_true: np.ndarray, y_pred: np.ndarray, tolerance: int = 2) -> float:
    """Compute boundary F1 for binary masks with pixel tolerance."""

    true_boundary = find_boundaries(y_true.astype(bool), mode="outer")
    pred_boundary = find_boundaries(y_pred.astype(bool), mode="outer")
    return _tolerant_f1(true_boundary, pred_boundary, tolerance)


def skeleton_f1(y_true: np.ndarray, y_pred: np.ndarray, tolerance: int = 1) -> float:
    """Compute skeleton F1 for binary masks."""

    true_skeleton = skeletonize(y_true.astype(bool))
    pred_skeleton = skeletonize(y_pred.astype(bool))
    return _tolerant_f1(true_skeleton, pred_skeleton, tolerance)


def component_count(mask: np.ndarray) -> int:
    """Count connected foreground components in a binary mask."""

    return int(label(mask.astype(bool), connectivity=2).max())


def component_count_error(y_true: np.ndarray, y_pred: np.ndarray) -> int:
    """Return absolute connected-component count error."""

    return abs(component_count(y_true) - component_count(y_pred))


def _tolerant_f1(y_true: np.ndarray, y_pred: np.ndarray, tolerance: int) -> float:
    true = y_true.astype(bool)
    pred = y_pred.astype(bool)
    if not true.any() and not pred.any():
        return 1.0
    if not true.any() or not pred.any():
        return 0.0
    structure = np.ones((2 * tolerance + 1, 2 * tolerance + 1), dtype=bool)
    true_dilated = binary_dilation(true, structure=structure)
    pred_dilated = binary_dilation(pred, structure=structure)
    precision = np.count_nonzero(pred & true_dilated) / max(np.count_nonzero(pred), 1)
    recall = np.count_nonzero(true & pred_dilated) / max(np.count_nonzero(true), 1)
    denom = precision + recall
    return float(2 * precision * recall / denom) if denom else 0.0
