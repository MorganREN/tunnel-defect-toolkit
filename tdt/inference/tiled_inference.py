"""Model-agnostic tiled inference wrapper."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from tdt.preprocessing.stitching import stitch_probabilities
from tdt.preprocessing.tiling import plan_tiles


def tiled_predict(
    image: np.ndarray,
    predict_fn: Callable[[np.ndarray], np.ndarray],
    tile_size: tuple[int, int],
    stride: tuple[int, int],
    merge: str = "gaussian",
) -> np.ndarray:
    """Run tiled prediction with a user-provided model callback.

    The callback must accept an image tile and return an H x W x C probability
    map for that tile.
    """

    height, width = image.shape[:2]
    tiles = plan_tiles(width, height, tile_size=tile_size, stride=stride)
    probabilities = []
    for tile in tiles:
        crop = image[tile.box.y0 : tile.box.y1, tile.box.x0 : tile.box.x1]
        probabilities.append(predict_fn(crop))
    return stitch_probabilities(tiles, probabilities, output_shape=(height, width), merge=merge)
