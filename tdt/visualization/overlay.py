"""Prediction and annotation overlay visualization."""

from __future__ import annotations

import numpy as np


def colorize_mask(mask: np.ndarray, color_map: dict[int, tuple[int, int, int]]) -> np.ndarray:
    """Convert a semantic mask into an RGB color image."""

    out = np.zeros((*mask.shape, 3), dtype=np.uint8)
    for class_id, color in color_map.items():
        out[mask == class_id] = color
    return out


def overlay_mask(
    image: np.ndarray,
    mask: np.ndarray,
    color_map: dict[int, tuple[int, int, int]],
    alpha: float = 0.45,
) -> np.ndarray:
    """Overlay a semantic mask on an RGB image."""

    base = image[..., :3].astype(np.float32)
    color = colorize_mask(mask, color_map).astype(np.float32)
    foreground = mask != 0
    out = base.copy()
    out[foreground] = (1.0 - alpha) * base[foreground] + alpha * color[foreground]
    return np.clip(out, 0, 255).astype(np.uint8)
