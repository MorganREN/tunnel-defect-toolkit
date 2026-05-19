"""Inference profiling helpers."""

from __future__ import annotations

from tdt.preprocessing.tiling import plan_tiles


def tile_count(width: int, height: int, tile_size: tuple[int, int], stride: tuple[int, int]) -> int:
    """Return the number of tiles required for an image."""

    return len(plan_tiles(width, height, tile_size=tile_size, stride=stride))
