"""Dataset validation utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images, read_mask


def validate_dataset(config: DatasetConfig) -> list[str]:
    """Return validation issues for a dataset config and its paths.

    An empty list means no blocking issue was detected.
    """

    issues: list[str] = []
    if not config.paths.images.exists():
        issues.append(f"Image directory does not exist: {config.paths.images}")
    if config.paths.masks is not None and not config.paths.masks.exists():
        issues.append(f"Mask directory does not exist: {config.paths.masks}")
    if config.paths.annotations is not None and not config.paths.annotations.exists():
        issues.append(f"Annotation directory does not exist: {config.paths.annotations}")
    if not config.classes:
        issues.append("No classes declared in config.")
    if len(config.class_ids) != len(config.classes):
        issues.append("Duplicate class ids found in config.")

    if config.paths.images.exists():
        images = list_images(config.paths.images)
        if not images:
            issues.append(f"No image files found in: {config.paths.images}")
        if config.paths.masks is not None and config.paths.masks.exists():
            masks = list_images(config.paths.masks)
            if not masks:
                issues.append(f"No mask files found in: {config.paths.masks}")
            missing = _missing_mask_stems(images, config.paths.masks)
            if missing:
                preview = ", ".join(missing[:5])
                issues.append(f"Missing masks for {len(missing)} image(s): {preview}")
            issues.extend(_validate_pairs(images, config.paths.masks, config))
    if config.paths.annotations is not None and config.paths.annotations.exists():
        if not any(config.paths.annotations.glob("*.json")):
            issues.append(f"No LabelMe JSON files found in: {config.paths.annotations}")
    return issues


def _missing_mask_stems(images: list[Path], mask_dir: Path) -> list[str]:
    mask_stems = {path.stem for path in list_images(mask_dir)}
    return [image.stem for image in images if image.stem not in mask_stems]


def _validate_pairs(images: list[Path], mask_dir: Path, config: DatasetConfig) -> list[str]:
    mask_by_stem = {path.stem: path for path in list_images(mask_dir)}
    issues: list[str] = []
    for image_path in images:
        mask_path = mask_by_stem.get(image_path.stem)
        try:
            with Image.open(image_path) as image:
                image_size = image.size
                image.verify()
        except (OSError, UnidentifiedImageError) as error:
            issues.append(f"Unreadable image file: {image_path} ({error})")
            continue
        if mask_path is None:
            continue
        try:
            with Image.open(mask_path) as mask_image:
                mask_size = mask_image.size
                mask_image.verify()
            mask = read_mask(mask_path)
        except (OSError, UnidentifiedImageError) as error:
            issues.append(f"Unreadable mask file: {mask_path} ({error})")
            continue
        if image_size != mask_size:
            issues.append(
                f"Image/mask size mismatch for {image_path.stem}: "
                f"image={image_size}, mask={mask_size}"
            )
        unknown = {int(value) for value in np.unique(mask)} - config.class_ids
        if config.ignore_index is not None:
            unknown.discard(int(config.ignore_index))
        if unknown:
            issues.append(f"Unknown class id(s) in mask {mask_path.name}: {sorted(unknown)}")
    return issues
