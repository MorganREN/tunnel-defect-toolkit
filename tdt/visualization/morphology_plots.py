"""Publication-oriented morphology plots."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd


def save_compactness_elongation_plot(frame: pd.DataFrame, output_path: str | Path) -> Path:
    """Save a compactness-elongation scatter plot."""

    _prepare_matplotlib_cache()
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4.8))
    for label, group in frame.groupby("class_name" if "class_name" in frame else "class_id"):
        ax.scatter(group["compactness"], group["elongation"], label=str(label), s=14, alpha=0.65)
    ax.set_xlabel("Compactness")
    ax.set_ylabel("Elongation")
    ax.set_yscale("log")
    ax.grid(True, linewidth=0.4, alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def save_morphology_boxplot(
    frame: pd.DataFrame,
    metric: str,
    output_path: str | Path,
    *,
    log_scale: bool = False,
) -> Path:
    """Save a class-wise boxplot for one morphology metric."""

    _prepare_matplotlib_cache()
    import matplotlib.pyplot as plt

    _require_columns(frame, ["class_name", metric])
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    labels = sorted(frame["class_name"].unique())
    data = [frame.loc[frame["class_name"] == label, metric].dropna().to_numpy() for label in labels]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.boxplot(data, labels=labels, showfliers=False, patch_artist=True)
    ax.set_xlabel("Defect class")
    ax.set_ylabel(_pretty_metric_name(metric))
    if log_scale:
        ax.set_yscale("log")
    ax.grid(axis="y", linewidth=0.4, alpha=0.25)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def save_morphology_count_plot(frame: pd.DataFrame, output_path: str | Path) -> Path:
    """Save a class-wise instance count bar plot."""

    _prepare_matplotlib_cache()
    import matplotlib.pyplot as plt

    _require_columns(frame, ["class_name"])
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = frame["class_name"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(counts.index, counts.values)
    ax.set_xlabel("Defect class")
    ax.set_ylabel("Connected instances")
    ax.grid(axis="y", linewidth=0.4, alpha=0.25)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def save_morphology_plots(
    csv_path: str | Path,
    output_dir: str | Path,
    *,
    formats: tuple[str, ...] = ("png",),
) -> list[Path]:
    """Generate a standard morphology figure set from descriptor CSV."""

    frame = pd.read_csv(csv_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []

    for suffix in formats:
        suffix = suffix.lstrip(".")
        outputs.append(save_compactness_elongation_plot(frame, out / f"compactness_elongation.{suffix}"))
        outputs.append(save_morphology_count_plot(frame, out / f"instance_counts.{suffix}"))
        outputs.append(
            save_morphology_boxplot(
                frame,
                "elongation",
                out / f"elongation_by_class.{suffix}",
                log_scale=True,
            )
        )
        outputs.append(
            save_morphology_boxplot(
                frame,
                "mean_width_px",
                out / f"mean_width_px_by_class.{suffix}",
                log_scale=True,
            )
        )
        outputs.append(
            save_morphology_boxplot(
                frame,
                "compactness",
                out / f"compactness_by_class.{suffix}",
            )
        )
        outputs.append(
            save_morphology_boxplot(
                frame,
                "solidity",
                out / f"solidity_by_class.{suffix}",
            )
        )
    return outputs


def _pretty_metric_name(metric: str) -> str:
    return metric.replace("_", " ").title()


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _prepare_matplotlib_cache() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "tdt-matplotlib"))
