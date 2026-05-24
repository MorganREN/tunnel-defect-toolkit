"""Dataset configuration schema.

The schema is intentionally small in V1. It standardizes enough metadata for
semantic-mask morphology analysis, quality inspection, paired tiling, and
reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ClassInfo:
    """Semantic class metadata."""

    id: int
    name: str
    color: tuple[int, int, int]
    morphology: str | None = None
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class DatasetPaths:
    """Filesystem locations for a dataset."""

    images: Path
    masks: Path | None = None
    annotations: Path | None = None
    splits: Path | None = None


@dataclass(frozen=True)
class DatasetConfig:
    """Validated dataset configuration."""

    name: str
    task: str
    paths: DatasetPaths
    classes: tuple[ClassInfo, ...]
    annotation_format: str | None = None
    background_id: int = 0
    ignore_index: int | None = 255
    tiling: dict[str, Any] | None = None
    analysis: dict[str, Any] | None = None

    @property
    def class_ids(self) -> set[int]:
        """Return all declared semantic class ids."""

        return {item.id for item in self.classes}

    @property
    def class_names(self) -> dict[int, str]:
        """Return a mapping from class id to readable class name."""

        return {item.id: item.name for item in self.classes}


def load_dataset_config(path: str | Path) -> DatasetConfig:
    """Load a YAML dataset configuration file.

    Parameters
    ----------
    path:
        Path to a dataset YAML file.

    Returns
    -------
    DatasetConfig
        Parsed and lightly validated configuration.
    """

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Dataset config does not exist: {config_path}")
    try:
        with config_path.open("r", encoding="utf-8") as stream:
            raw = yaml.safe_load(stream)
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML dataset config: {config_path}") from error
    if not isinstance(raw, dict):
        raise ValueError(f"Dataset config must contain a YAML mapping: {config_path}")
    if "name" not in raw:
        raise ValueError("Dataset config requires a 'name' field.")

    root = config_path.parent.parent if config_path.parent.name == "configs" else config_path.parent
    paths_raw = raw.get("paths", {})
    if not isinstance(paths_raw, dict) or "images" not in paths_raw:
        raise ValueError("Dataset config requires paths.images.")
    paths = DatasetPaths(
        images=_resolve_path(root, paths_raw["images"]),
        masks=_resolve_optional_path(root, paths_raw.get("masks")),
        annotations=_resolve_optional_path(root, paths_raw.get("annotations")),
        splits=_resolve_optional_path(root, paths_raw.get("splits")),
    )

    classes_raw = raw.get("classes", [])
    if not isinstance(classes_raw, list):
        raise ValueError("Dataset config field 'classes' must be a list.")
    classes: list[ClassInfo] = []
    for index, item in enumerate(classes_raw):
        if not isinstance(item, dict) or "id" not in item or "name" not in item:
            raise ValueError(f"Class entry {index} requires 'id' and 'name'.")
        color = tuple(int(v) for v in item.get("color", [0, 0, 0]))
        if len(color) != 3 or any(channel < 0 or channel > 255 for channel in color):
            raise ValueError(f"Class entry {index} color must contain three values from 0 to 255.")
        classes.append(
            ClassInfo(
                id=int(item["id"]),
                name=str(item["name"]),
                color=color,
                morphology=item.get("morphology"),
                aliases=tuple(str(alias) for alias in item.get("aliases", [])),
            )
        )

    annotation = raw.get("annotation", {})
    if not isinstance(annotation, dict):
        raise ValueError("Dataset config field 'annotation' must be a mapping.")
    analysis = raw.get("analysis", {})
    if not isinstance(analysis, dict):
        raise ValueError("Dataset config field 'analysis' must be a mapping.")
    return DatasetConfig(
        name=str(raw["name"]),
        task=str(raw.get("task", "semantic_segmentation")),
        paths=paths,
        classes=tuple(classes),
        annotation_format=annotation.get("format"),
        background_id=int(annotation.get("background_id", 0)),
        ignore_index=analysis.get("ignore_index", 255),
        tiling=raw.get("tiling"),
        analysis=analysis,
    )


def _resolve_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _resolve_optional_path(root: Path, value: str | Path | None) -> Path | None:
    if value is None:
        return None
    return _resolve_path(root, value)
