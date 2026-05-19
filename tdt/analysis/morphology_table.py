"""Tabular morphology profiling."""

from __future__ import annotations

import os
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from tdt.analysis.morphology import describe_instances
from tdt.datasets.schema import DatasetConfig
from tdt.utils.io import list_images, read_mask
from tdt.utils.progress import progress


def morphology_table(
    config: DatasetConfig,
    show_progress: bool = True,
    workers: int | str = 1,
) -> pd.DataFrame:
    """Compute instance-level morphology descriptors for all masks."""

    if config.paths.masks is None:
        raise ValueError("morphology_table requires config.paths.masks.")

    class_name = config.class_names
    foreground_ids = {item.id for item in config.classes if item.id != config.background_id}
    mask_paths = list_images(config.paths.masks)
    worker_count = resolve_worker_count(workers)

    if worker_count <= 1:
        rows = []
        for mask_path in progress(
            mask_paths,
            total=len(mask_paths),
            desc="Morphology descriptors",
            enabled=show_progress,
        ):
            rows.extend(_describe_mask(mask_path, foreground_ids, class_name))
        return _to_sorted_frame(rows)

    rows = _parallel_morphology(mask_paths, foreground_ids, class_name, worker_count, show_progress)
    return _to_sorted_frame(rows)


def resolve_worker_count(workers: int | str) -> int:
    """Resolve a user worker argument into a conservative process count."""

    if isinstance(workers, str):
        value = workers.strip().lower()
        if value == "auto":
            cpu_count = os.cpu_count() or 2
            return max(1, min(cpu_count - 1, 4))
        try:
            workers = int(value)
        except ValueError as error:
            raise ValueError("workers must be an integer or 'auto'.") from error
    return max(1, int(workers))


def _parallel_morphology(
    mask_paths: list[Path],
    foreground_ids: set[int],
    class_name: dict[int, str],
    workers: int,
    show_progress: bool,
) -> list[dict]:
    rows: list[dict] = []
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(_describe_mask, mask_path, foreground_ids, class_name)
                for mask_path in mask_paths
            ]
            for future in progress(
                as_completed(futures),
                total=len(futures),
                desc=f"Morphology x{workers}",
                enabled=show_progress,
            ):
                rows.extend(future.result())
    except (OSError, PermissionError) as error:
        warnings.warn(
            f"Process-based morphology parallelism is unavailable ({error}); "
            "falling back to single-process execution.",
            RuntimeWarning,
            stacklevel=2,
        )
        for mask_path in progress(
            mask_paths,
            total=len(mask_paths),
            desc="Morphology descriptors",
            enabled=show_progress,
        ):
            rows.extend(_describe_mask(mask_path, foreground_ids, class_name))
    return rows


def _describe_mask(
    mask_path: Path,
    foreground_ids: set[int],
    class_name: dict[int, str],
) -> list[dict]:
    mask = read_mask(mask_path)
    rows = []
    for descriptor in describe_instances(mask, foreground_ids):
        row = asdict(descriptor)
        row["image_id"] = mask_path.stem
        row["class_name"] = class_name.get(descriptor.class_id, str(descriptor.class_id))
        rows.append(row)
    return rows


def _to_sorted_frame(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    return frame.sort_values(["image_id", "class_id", "instance_id"]).reset_index(drop=True)
