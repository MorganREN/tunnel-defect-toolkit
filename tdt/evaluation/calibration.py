"""Calibration and uncertainty metrics."""

from __future__ import annotations

import numpy as np


def entropy(probabilities: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Compute categorical entropy from class probabilities."""

    probs = np.clip(probabilities, eps, 1.0)
    return -np.sum(probs * np.log(probs), axis=-1)


def expected_calibration_error(
    confidences: np.ndarray,
    correct: np.ndarray,
    n_bins: int = 15,
) -> float:
    """Compute expected calibration error."""

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total = max(confidences.size, 1)
    for low, high in zip(bins[:-1], bins[1:]):
        in_bin = (confidences >= low) & (confidences < high)
        if not in_bin.any():
            continue
        accuracy = float(correct[in_bin].mean())
        confidence = float(confidences[in_bin].mean())
        ece += float(in_bin.sum()) / total * abs(accuracy - confidence)
    return ece
