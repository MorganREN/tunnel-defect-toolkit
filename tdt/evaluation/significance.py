"""Statistical significance helpers for benchmark comparisons."""

from __future__ import annotations

import numpy as np


def bootstrap_mean_ci(
    values: np.ndarray,
    n_bootstrap: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Return mean and bootstrap confidence interval."""

    arr = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(arr, size=arr.size, replace=True).mean() for _ in range(n_bootstrap)])
    alpha = (1.0 - confidence) / 2.0
    return float(arr.mean()), float(np.quantile(means, alpha)), float(np.quantile(means, 1.0 - alpha))
