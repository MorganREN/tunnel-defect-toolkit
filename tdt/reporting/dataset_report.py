"""Dataset report generation."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

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
    quality = pd.DataFrame(
        [asdict(issue) for issue in check_mask_quality(config, show_progress=show_progress)]
    )

    distribution.to_csv(out / "class_distribution.csv", index=False)
    resolutions.to_csv(out / "resolution_table.csv", index=False)
    quality.to_csv(out / "quality_issues.csv", index=False)

    sections = {
        "Class Distribution": dataframe_to_html_table(distribution),
        "Resolution Table": dataframe_to_html_table(resolutions),
        "Quality Issues": dataframe_to_html_table(quality if not quality.empty else pd.DataFrame()),
    }
    if with_morphology:
        morphology = morphology_table(
            config,
            show_progress=show_progress,
            workers=morphology_workers,
        )
        morphology.to_csv(out / "morphology_descriptors.csv", index=False)
        sections["Morphology Summary"] = dataframe_to_html_table(_morphology_summary(morphology))
    report_path = out / "dataset_report.html"
    write_report(f"{config.name} Dataset Report", sections, report_path)
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
