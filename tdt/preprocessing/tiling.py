"""Resolution-adaptive tiling utilities."""

from __future__ import annotations

from dataclasses import dataclass

from tdt.utils.geometry import Box


@dataclass(frozen=True)
class Tile:
    """One tile record."""

    tile_id: str
    source_id: str
    box: Box
    width: int
    height: int


def plan_tiles(
    width: int,
    height: int,
    tile_size: tuple[int, int],
    stride: tuple[int, int],
    source_id: str = "image",
) -> list[Tile]:
    """Plan overlapping tiles that cover an image."""

    tile_w, tile_h = tile_size
    stride_x, stride_y = stride
    xs = _positions(width, tile_w, stride_x)
    ys = _positions(height, tile_h, stride_y)
    tiles: list[Tile] = []
    for row, y0 in enumerate(ys):
        for col, x0 in enumerate(xs):
            x1 = min(x0 + tile_w, width)
            y1 = min(y0 + tile_h, height)
            tiles.append(
                Tile(
                    tile_id=f"{source_id}_r{row:03d}_c{col:03d}",
                    source_id=source_id,
                    box=Box(x0=x0, y0=y0, x1=x1, y1=y1),
                    width=x1 - x0,
                    height=y1 - y0,
                )
            )
    return tiles


def recommend_tile_plan(width: int, height: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """Recommend tile size and stride from image resolution.

    The heuristic is intentionally simple in V1 and should be made dataset-
    specific through configs for formal experiments.
    """

    pixels = width * height
    if pixels < 512 * 512:
        return (width, height), (width, height)
    if pixels < 2048 * 2048:
        return (768, 768), (576, 576)
    return (1024, 1024), (768, 768)


def _positions(length: int, tile_length: int, stride: int) -> list[int]:
    if tile_length >= length:
        return [0]
    positions = list(range(0, max(length - tile_length + 1, 1), stride))
    last = length - tile_length
    if positions[-1] != last:
        positions.append(last)
    return positions
