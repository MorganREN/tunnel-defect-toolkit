"""Evaluation report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from tdt.reporting.html import dataframe_to_html_table, write_report


def generate_evaluation_report(metrics: pd.DataFrame, output_dir: str | Path, title: str) -> Path:
    """Generate a simple HTML evaluation report from a metric table."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(out / "metrics.csv", index=False)
    report_path = out / "evaluation_report.html"
    write_report(title, {"Metrics": dataframe_to_html_table(metrics)}, report_path)
    return report_path
