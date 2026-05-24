"""Batch overlay export."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from tdt.datasets.manifest import collect_dataset_items
from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import read_image, read_mask
from tdt.utils.progress import progress
from tdt.visualization.overlay import overlay_mask


def export_mask_overlays(
    config: DatasetConfig,
    output_dir: str | Path,
    *,
    limit: int | None = None,
    alpha: float = 0.45,
    show_progress: bool = True,
) -> list[Path]:
    """Export image/mask overlay PNGs for a configured dataset."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    color_map = {item.id: item.color for item in config.classes}
    items = collect_dataset_items(config, require_masks=True)
    if limit is not None:
        items = items[:limit]

    outputs: list[Path] = []
    for item in progress(items, total=len(items), desc="Overlay export", enabled=show_progress):
        if item.mask_path is None:
            raise FileNotFoundError(f"Missing mask for overlay item: {item.image_id}")
        image = read_image(item.image_path)
        mask = read_mask(item.mask_path)
        overlay = overlay_mask(
            image,
            mask,
            color_map=color_map,
            alpha=alpha,
            background_id=config.background_id,
        )
        output_path = out / f"{item.image_id}_overlay.png"
        Image.fromarray(overlay).save(output_path)
        outputs.append(output_path)
    return outputs
