"""Model-agnostic segmentation metrics."""

from __future__ import annotations

import numpy as np


def confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    num_classes: int,
    ignore_index: int | None = 255,
) -> np.ndarray:
    """Compute a pixel-level confusion matrix."""

    true = np.asarray(y_true).reshape(-1)
    pred = np.asarray(y_pred).reshape(-1)
    valid = (true >= 0) & (true < num_classes) & (pred >= 0) & (pred < num_classes)
    if ignore_index is not None:
        valid &= true != ignore_index
    encoded = num_classes * true[valid].astype(int) + pred[valid].astype(int)
    return np.bincount(encoded, minlength=num_classes**2).reshape(num_classes, num_classes)


def per_class_iou(matrix: np.ndarray) -> np.ndarray:
    """Compute per-class IoU from a confusion matrix."""

    tp = np.diag(matrix)
    denom = matrix.sum(axis=1) + matrix.sum(axis=0) - tp
    return np.divide(tp, denom, out=np.zeros_like(tp, dtype=float), where=denom > 0)


def per_class_dice(matrix: np.ndarray) -> np.ndarray:
    """Compute per-class Dice from a confusion matrix."""

    tp = np.diag(matrix)
    denom = matrix.sum(axis=1) + matrix.sum(axis=0)
    return np.divide(2 * tp, denom, out=np.zeros_like(tp, dtype=float), where=denom > 0)


def image_level_f1(y_true: np.ndarray, y_pred: np.ndarray, class_ids: list[int]) -> float:
    """Compute image-level macro F1 over class presence."""

    scores = []
    true_values = set(int(v) for v in np.unique(y_true))
    pred_values = set(int(v) for v in np.unique(y_pred))
    for class_id in class_ids:
        gt = class_id in true_values
        pr = class_id in pred_values
        tp = int(gt and pr)
        fp = int((not gt) and pr)
        fn = int(gt and (not pr))
        denom = 2 * tp + fp + fn
        scores.append((2 * tp / denom) if denom else 1.0)
    return float(np.mean(scores)) if scores else 0.0
