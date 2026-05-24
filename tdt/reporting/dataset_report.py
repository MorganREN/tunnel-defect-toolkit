"""Dataset report generation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import pandas as pd

from tdt import __version__
from tdt.analysis.cooccurrence import cooccurrence_matrix
from tdt.analysis.distribution import class_distribution
from tdt.analysis.morphology_table import morphology_table
from tdt.analysis.quality import check_mask_quality
from tdt.analysis.resolution import resolution_table
from tdt.datasets.manifest import collect_dataset_items
from tdt.datasets.schema import DatasetConfig
from tdt.reporting.html import dataframe_to_html_table, write_report


def generate_dataset_report(
    config: DatasetConfig,
    output_dir: str | Path,
    with_morphology: bool = False,
    show_progress: bool = True,
    morphology_workers: int | str = 1,
    morphology_connectivity: int | None = None,
    morphology_min_area_px: int | None = None,
) -> Path:
    """Generate CSV and HTML dataset analysis artifacts."""

    started_at = datetime.now(timezone.utc)
    started = perf_counter()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    analysis_settings = config.analysis or {}
    morphology_settings = analysis_settings.get("morphology", {})
    if not isinstance(morphology_settings, dict):
        raise ValueError("analysis.morphology must be a mapping.")
    connectivity = int(
        morphology_connectivity
        if morphology_connectivity is not None
        else morphology_settings.get("connectivity", 2)
    )
    min_area_px = int(
        morphology_min_area_px
        if morphology_min_area_px is not None
        else morphology_settings.get("min_area_px", 1)
    )
    min_foreground_px = int(analysis_settings.get("min_foreground_px", 4))

    distribution = class_distribution(config, show_progress=show_progress)
    resolutions = resolution_table(config, show_progress=show_progress)
    resolution_summary = _resolution_summary(resolutions)
    cooccurrence = cooccurrence_matrix(config)
    quality = pd.DataFrame(
        [
            asdict(issue)
            for issue in check_mask_quality(
                config,
                min_foreground_pixels=min_foreground_px,
                show_progress=show_progress,
            )
        ],
        columns=["image_id", "issue", "detail"],
    )
    quality_summary = _quality_summary(quality)

    distribution.to_csv(out / "class_distribution.csv", index=False)
    resolutions.to_csv(out / "resolution_table.csv", index=False)
    resolution_summary.to_csv(out / "resolution_summary.csv", index=False)
    cooccurrence.to_csv(out / "cooccurrence_matrix.csv")
    quality.to_csv(out / "quality_issues.csv", index=False)
    quality_summary.to_csv(out / "quality_summary.csv", index=False)

    sections = {
        "Class Distribution": dataframe_to_html_table(distribution),
        "Resolution Summary": dataframe_to_html_table(resolution_summary),
        "Resolution Table": dataframe_to_html_table(resolutions),
        "Co-occurrence Matrix": cooccurrence.to_html(escape=True, border=0),
        "Quality Summary": dataframe_to_html_table(quality_summary),
        "Quality Issues": dataframe_to_html_table(quality if not quality.empty else pd.DataFrame()),
    }
    if with_morphology:
        morphology = morphology_table(
            config,
            show_progress=show_progress,
            workers=morphology_workers,
            connectivity=connectivity,
            min_area_px=min_area_px,
        )
        morphology_summary = _morphology_summary(morphology)
        morphology.to_csv(out / "morphology_descriptors.csv", index=False)
        morphology_summary.to_csv(out / "morphology_summary.csv", index=False)
        sections["Morphology Summary"] = dataframe_to_html_table(morphology_summary)
    report_path = out / "dataset_report.html"
    write_report(f"{config.name} Dataset Report", sections, report_path)
    metadata = _analysis_metadata(
        config,
        started_at=started_at,
        duration_seconds=perf_counter() - started,
        with_morphology=with_morphology,
        connectivity=connectivity,
        min_area_px=min_area_px,
        min_foreground_px=min_foreground_px,
    )
    (out / "analysis_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_dataset_card(
        config,
        out,
        distribution,
        resolution_summary,
        quality_summary,
        morphology_policy=metadata["morphology_policy"] if with_morphology else None,
    )
    return report_path


def _morphology_summary(morphology: pd.DataFrame) -> pd.DataFrame:
    if morphology.empty:
        return pd.DataFrame(
            columns=[
                "class_name",
                "instances",
                "compactness_mean",
                "elongation_median",
                "solidity_mean",
                "skeleton_length_px_median",
                "mean_width_px_median",
            ]
        )
    return (
        morphology.groupby("class_name")
        .agg(
            instances=("instance_id", "count"),
            compactness_mean=("compactness", "mean"),
            elongation_median=("elongation", "median"),
            solidity_mean=("solidity", "mean"),
            skeleton_length_px_median=("skeleton_length_px", "median"),
            mean_width_px_median=("mean_width_px", "median"),
        )
        .reset_index()
    )


def _resolution_summary(resolutions: pd.DataFrame) -> pd.DataFrame:
    if resolutions.empty:
        return resolutions
    return (
        resolutions.groupby("resolution_group")
        .agg(
            images=("image_id", "count"),
            width_median=("width", "median"),
            height_median=("height", "median"),
            megapixels_median=("megapixels", "median"),
            megapixels_max=("megapixels", "max"),
        )
        .reset_index()
    )


def _quality_summary(quality: pd.DataFrame) -> pd.DataFrame:
    if quality.empty:
        return pd.DataFrame([{"issue": "none", "count": 0}])
    return quality.groupby("issue").size().reset_index(name="count")


def _write_dataset_card(
    config: DatasetConfig,
    output_dir: Path,
    distribution: pd.DataFrame,
    resolution_summary: pd.DataFrame,
    quality_summary: pd.DataFrame,
    morphology_policy: dict[str, object] | None = None,
) -> Path:
    foreground = distribution[distribution["class_id"] != config.background_id]
    lines = [
        f"# {config.name} Dataset Card",
        "",
        f"- Task: `{config.task}`",
        f"- Classes: {len(config.classes)}",
        f"- Foreground classes: {max(len(config.classes) - 1, 0)}",
        f"- Total foreground pixels: {int(foreground['pixel_count'].sum()) if not foreground.empty else 0}",
        "",
        "## Class Distribution",
        "",
        _markdown_table(distribution),
        "",
        "## Resolution Summary",
        "",
        _markdown_table(resolution_summary),
        "",
        "## Quality Summary",
        "",
        _markdown_table(quality_summary),
        "",
    ]
    if morphology_policy is not None:
        lines.extend(
            [
                "## Morphology Policy",
                "",
                f"- Units: `{morphology_policy['units']}`",
                f"- Connectivity: `{morphology_policy['connectivity']}`",
                f"- Minimum region area: `{morphology_policy['min_area_px']} px`",
                "- Same-class touching regions are represented as one connected region.",
                "",
            ]
        )
    output = output_dir / "dataset_card.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _analysis_metadata(
    config: DatasetConfig,
    *,
    started_at: datetime,
    duration_seconds: float,
    with_morphology: bool,
    connectivity: int,
    min_area_px: int,
    min_foreground_px: int,
) -> dict[str, Any]:
    items = collect_dataset_items(config, require_masks=False)
    manifest_records = [
        {
            "image_id": item.image_id,
            "image_file": item.image_path.name,
            "mask_file": item.mask_path.name if item.mask_path is not None else None,
        }
        for item in items
    ]
    payload = json.dumps(manifest_records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema_version": "tdt-analysis-metadata-v1",
        "tool": {"name": "tunnel-defect-toolkit", "version": __version__},
        "dataset": {
            "name": config.name,
            "task": config.task,
            "annotation_format": config.annotation_format,
            "background_id": config.background_id,
            "ignore_index": config.ignore_index,
            "classes": [
                {"id": class_info.id, "name": class_info.name}
                for class_info in config.classes
            ],
        },
        "input_manifest": {
            "image_count": len(items),
            "paired_mask_count": sum(item.mask_path is not None for item in items),
            "sha256": hashlib.sha256(payload).hexdigest(),
        },
        "quality_policy": {"min_foreground_px": min_foreground_px},
        "morphology_policy": {
            "enabled": with_morphology,
            "units": "pixels",
            "connectivity": connectivity,
            "min_area_px": min_area_px,
            "touching_same_class_regions": "single_connected_region",
        },
        "run": {
            "started_at_utc": started_at.isoformat(),
            "duration_seconds": round(duration_seconds, 6),
        },
    }


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    columns = [str(column) for column in frame.columns]
    rows = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        rows.append("| " + " | ".join(str(row[column]) for column in frame.columns) + " |")
    return "\n".join(rows)
