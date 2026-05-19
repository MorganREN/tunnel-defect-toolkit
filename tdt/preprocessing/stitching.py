"""Tile stitching utilities."""

from __future__ import annotations

import numpy as np

from tdt.preprocessing.tiling import Tile


def gaussian_weight(shape: tuple[int, int], sigma_scale: float = 0.25) -> np.ndarray:
    """Create a 2D Gaussian blending weight map."""

    height, width = shape
    y = np.linspace(-1.0, 1.0, height)
    x = np.linspace(-1.0, 1.0, width)
    yy, xx = np.meshgrid(y, x, indexing="ij")
    sigma = sigma_scale
    weights = np.exp(-0.5 * (xx * xx + yy * yy) / (sigma * sigma))
    return weights / max(float(weights.max()), 1e-8)


def stitch_probabilities(
    tiles: list[Tile],
    probabilities: list[np.ndarray],
    output_shape: tuple[int, int],
    merge: str = "gaussian",
) -> np.ndarray:
    """Merge tile probability maps into one full-resolution probability map."""

    if len(tiles) != len(probabilities):
        raise ValueError("tiles and probabilities must have the same length.")

    height, width = output_shape
    channels = probabilities[0].shape[-1]
    canvas = np.zeros((height, width, channels), dtype=np.float64)
    normalizer = np.zeros((height, width, 1), dtype=np.float64)

    for tile, prob in zip(tiles, probabilities):
        tile_h, tile_w = prob.shape[:2]
        weight = np.ones((tile_h, tile_w, 1), dtype=np.float64)
        if merge == "gaussian":
            weight = gaussian_weight((tile_h, tile_w))[..., None]
        canvas[tile.box.y0 : tile.box.y1, tile.box.x0 : tile.box.x1] += prob * weight
        normalizer[tile.box.y0 : tile.box.y1, tile.box.x0 : tile.box.x1] += weight

    return canvas / np.maximum(normalizer, 1e-8)
