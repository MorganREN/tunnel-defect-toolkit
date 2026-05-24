"""Dataset manifest helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images

MANIFEST_SCHEMA_VERSION = "tdt-manifest-v1"


@dataclass(frozen=True)
class DatasetItem:
    """One source image and optional paired mask."""

    image_id: str
    image_path: Path
    mask_path: Path | None = None
    split: str | None = None


def collect_dataset_items(config: DatasetConfig, require_masks: bool = False) -> list[DatasetItem]:
    """Collect source images with optional same-stem semantic masks.

    If multiple image files share a stem, the lexicographically first path is
    used. This keeps mixed `.jpg` / `.png` raw folders deterministic.
    """

    image_by_stem = _first_path_by_stem(list_images(config.paths.images))
    if not image_by_stem:
        raise ValueError(f"No image files found in: {config.paths.images}")
    mask_by_stem: dict[str, Path] = {}
    if config.paths.masks is not None and config.paths.masks.exists():
        mask_by_stem = _first_path_by_stem(list_images(config.paths.masks))

    stems = sorted(image_by_stem)
    if require_masks:
        missing = [stem for stem in stems if stem not in mask_by_stem]
        if missing:
            preview = ", ".join(missing[:5])
            raise FileNotFoundError(f"Missing masks for {len(missing)} image(s): {preview}")

    return [
        DatasetItem(
            image_id=stem,
            image_path=image_by_stem[stem],
            mask_path=mask_by_stem.get(stem),
        )
        for stem in stems
    ]


def items_to_dataframe(items: list[DatasetItem]) -> pd.DataFrame:
    """Convert dataset items to a serializable DataFrame."""

    rows = []
    for item in items:
        row = asdict(item)
        row["schema_version"] = MANIFEST_SCHEMA_VERSION
        row["image_path"] = str(item.image_path)
        row["mask_path"] = str(item.mask_path) if item.mask_path is not None else ""
        rows.append(row)
    return pd.DataFrame(rows)


def write_manifest(items: list[DatasetItem], output_path: str | Path) -> Path:
    """Write dataset items as CSV manifest."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    items_to_dataframe(items).to_csv(output, index=False)
    return output


def _first_path_by_stem(paths: list[Path]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(paths):
        result.setdefault(path.stem, path)
    return result
