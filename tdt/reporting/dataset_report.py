"""Dataset report generation."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from tdt.analysis.cooccurrence import cooccurrence_matrix
from tdt.analysis.distribution import class_distribution
from tdt.analysis.morphology_table import morphology_table
from tdt.analysis.quality import check_mask_quality
from tdt.analysis.resolution import resolution_table
from tdt.datasets.schema import DatasetConfig
from tdt.reporting.html import dataframe_to_html_table, write_report


def generate_dataset_report(
    config: DatasetConfig,
    output_dir: str | Path,
    with_morphology: bool = False,
    show_progress: bool = True,
    morphology_workers: int | str = 1,
) -> Path:
    """Generate CSV and HTML dataset analysis artifacts."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    distribution = class_distribution(config, show_progress=show_progress)
    resolutions = resolution_table(config, show_progress=show_progress)
    resolution_summary = _resolution_summary(resolutions)
    cooccurrence = cooccurrence_matrix(config)
    quality = pd.DataFrame(
        [asdict(issue) for issue in check_mask_quality(config, show_progress=show_progress)]
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
        )
        morphology_summary = _morphology_summary(morphology)
        morphology.to_csv(out / "morphology_descriptors.csv", index=False)
        morphology_summary.to_csv(out / "morphology_summary.csv", index=False)
        sections["Morphology Summary"] = dataframe_to_html_table(morphology_summary)
    report_path = out / "dataset_report.html"
    write_report(f"{config.name} Dataset Report", sections, report_path)
    _write_dataset_card(config, out, distribution, resolution_summary, quality_summary)
    return report_path


def _morphology_summary(morphology: pd.DataFrame) -> pd.DataFrame:
    if morphology.empty:
        return morphology
    return (
        morphology.groupby("class_name")
        .agg(
            instances=("instance_id", "count"),
            compactness_mean=("compactness", "mean"),
            elongation_median=("elongation", "median"),
            solidity_mean=("solidity", "mean"),
            skeleton_length_median=("skeleton_length", "median"),
            mean_width_median=("mean_width", "median"),
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
    output = output_dir / "dataset_card.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


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
