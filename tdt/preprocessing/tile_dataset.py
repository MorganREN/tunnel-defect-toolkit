"""Dataset tiling workflow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image

from tdt.datasets.manifest import collect_dataset_items
from tdt.datasets.schema import DatasetConfig
from tdt.preprocessing.tiling import plan_tiles, recommend_tile_plan
from tdt.utils.progress import progress

TILE_MANIFEST_SCHEMA_VERSION = "tdt-tile-manifest-v1"


def tile_dataset(
    config: DatasetConfig,
    output_dir: str | Path,
    tile_size: tuple[int, int] | None = None,
    stride: tuple[int, int] | None = None,
    splits_csv: str | Path | None = None,
    require_splits: bool = False,
    show_progress: bool = True,
) -> Path:
    """Generate image/mask tiles and a tile manifest CSV."""

    out = Path(output_dir)
    image_out = out / "images"
    mask_out = out / "masks"
    image_out.mkdir(parents=True, exist_ok=True)
    mask_out.mkdir(parents=True, exist_ok=True)

    items = collect_dataset_items(config, require_masks=True)
    split_by_id = _load_splits(splits_csv or _default_splits_path(config), require_splits)
    rows = []
    for item in progress(items, total=len(items), desc="Tiling dataset", enabled=show_progress):
        with Image.open(item.image_path) as image, Image.open(item.mask_path) as mask:
            width, height = image.size
            selected_tile_size, selected_stride = _resolve_tile_plan(width, height, tile_size, stride)
            split = split_by_id.get(item.image_id, "unsplit")
            item_image_out = image_out / split
            item_mask_out = mask_out / split
            item_image_out.mkdir(parents=True, exist_ok=True)
            item_mask_out.mkdir(parents=True, exist_ok=True)
            tiles = plan_tiles(
                width,
                height,
                tile_size=selected_tile_size,
                stride=selected_stride,
                source_id=item.image_id,
            )
            for tile in tiles:
                image_tile = image.crop((tile.box.x0, tile.box.y0, tile.box.x1, tile.box.y1))
                mask_tile = mask.crop((tile.box.x0, tile.box.y0, tile.box.x1, tile.box.y1))
                image_path = item_image_out / f"{tile.tile_id}.png"
                mask_path = item_mask_out / f"{tile.tile_id}.png"
                image_tile.save(image_path)
                mask_tile.save(mask_path)
                rows.append(
                    {
                        "schema_version": TILE_MANIFEST_SCHEMA_VERSION,
                        "tile_id": tile.tile_id,
                        "source_id": item.image_id,
                        "split": split,
                        "image_path": str(image_path),
                        "mask_path": str(mask_path),
                        "x0": tile.box.x0,
                        "y0": tile.box.y0,
                        "x1": tile.box.x1,
                        "y1": tile.box.y1,
                        "tile_width": tile.width,
                        "tile_height": tile.height,
                        "source_width": width,
                        "source_height": height,
                        "tile_size": f"{selected_tile_size[0]}x{selected_tile_size[1]}",
                        "stride": f"{selected_stride[0]}x{selected_stride[1]}",
                    }
                )

    manifest_path = out / "tile_manifest.csv"
    pd.DataFrame(rows).to_csv(manifest_path, index=False)
    return manifest_path


def _default_splits_path(config: DatasetConfig) -> Path | None:
    if config.paths.splits is None:
        return None
    candidate = config.paths.splits / "splits.csv"
    return candidate if candidate.exists() else None


def _load_splits(splits_csv: str | Path | None, require_splits: bool) -> dict[str, str]:
    if splits_csv is None:
        if require_splits:
            raise FileNotFoundError("Split-aware tiling requires --splits or config.paths.splits.")
        return {}
    path = Path(splits_csv)
    if not path.exists():
        if require_splits:
            raise FileNotFoundError(f"Split file does not exist: {path}")
        return {}
    frame = pd.read_csv(path)
    required = {"image_id", "split"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Split file is missing columns: {sorted(missing)}")
    return dict(zip(frame["image_id"].astype(str), frame["split"].astype(str)))


def _resolve_tile_plan(
    width: int,
    height: int,
    tile_size: tuple[int, int] | None,
    stride: tuple[int, int] | None,
) -> tuple[tuple[int, int], tuple[int, int]]:
    if tile_size is None:
        recommended_tile_size, recommended_stride = recommend_tile_plan(width, height)
        return recommended_tile_size, stride or recommended_stride
    return tile_size, stride or tile_size
