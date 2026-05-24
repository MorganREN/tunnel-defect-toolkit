"""IO helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".ppm", ".pgm"}


def list_images(path: str | Path) -> list[Path]:
    """List image-like files in a directory."""

    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Image directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected an image directory: {root}")
    return sorted(file for file in root.iterdir() if file.suffix.lower() in IMAGE_EXTENSIONS)


def read_image(path: str | Path) -> np.ndarray:
    """Read an image as a NumPy array."""

    with Image.open(path) as image:
        return np.asarray(image)


def read_mask(path: str | Path) -> np.ndarray:
    """Read a semantic mask as a 2D integer array."""

    with Image.open(path) as image:
        mask = np.asarray(image)
    if mask.ndim == 3:
        mask = mask[..., 0]
    return mask.astype(np.int64, copy=False)


def save_mask(mask: np.ndarray, path: str | Path) -> None:
    """Save a 2D semantic mask as an 8-bit image."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask.astype(np.uint8)).save(output)
