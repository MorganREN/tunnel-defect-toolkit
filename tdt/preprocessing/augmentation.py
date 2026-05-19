"""Lightweight augmentation placeholders for dataset experiments."""

from __future__ import annotations

import numpy as np


def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
    """Scale image brightness and clip to uint8 range."""

    return np.clip(image.astype(np.float32) * factor, 0, 255).astype(np.uint8)


def add_gaussian_noise(image: np.ndarray, sigma: float, seed: int | None = None) -> np.ndarray:
    """Add Gaussian noise to an image."""

    rng = np.random.default_rng(seed)
    noisy = image.astype(np.float32) + rng.normal(0.0, sigma, size=image.shape)
    return np.clip(noisy, 0, 255).astype(np.uint8)
