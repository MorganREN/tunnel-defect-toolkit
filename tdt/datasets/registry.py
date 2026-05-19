"""Dataset config registry helpers."""

from __future__ import annotations

from pathlib import Path

from tdt.datasets.schema import DatasetConfig, load_dataset_config


def load_config(config_path: str | Path) -> DatasetConfig:
    """Load a dataset config from disk."""

    return load_dataset_config(config_path)


def list_configs(config_dir: str | Path = "configs") -> list[Path]:
    """List YAML dataset configs in a directory."""

    root = Path(config_dir)
    return sorted([*root.glob("*.yaml"), *root.glob("*.yml")])
