"""Dataset validation utilities."""

from __future__ import annotations

from pathlib import Path

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images


def validate_dataset(config: DatasetConfig) -> list[str]:
    """Return validation issues for a dataset config and its paths.

    An empty list means no blocking issue was detected.
    """

    issues: list[str] = []
    if not config.paths.images.exists():
        issues.append(f"Image directory does not exist: {config.paths.images}")
    if config.paths.masks is not None and not config.paths.masks.exists():
        issues.append(f"Mask directory does not exist: {config.paths.masks}")
    if not config.classes:
        issues.append("No classes declared in config.")
    if len(config.class_ids) != len(config.classes):
        issues.append("Duplicate class ids found in config.")

    if config.paths.images.exists():
        images = list_images(config.paths.images)
        if not images:
            issues.append(f"No image files found in: {config.paths.images}")
        if config.paths.masks is not None and config.paths.masks.exists():
            missing = _missing_mask_stems(images, config.paths.masks)
            if missing:
                preview = ", ".join(missing[:5])
                issues.append(f"Missing masks for {len(missing)} image(s): {preview}")
    return issues


def _missing_mask_stems(images: list[Path], mask_dir: Path) -> list[str]:
    mask_stems = {path.stem for path in list_images(mask_dir)}
    return [image.stem for image in images if image.stem not in mask_stems]
