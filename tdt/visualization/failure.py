"""Failure case selection helpers."""

from __future__ import annotations

import pandas as pd


def select_worst_cases(metric_table: pd.DataFrame, metric: str, n: int = 12) -> pd.DataFrame:
    """Return the lowest-scoring examples for a metric."""

    return metric_table.sort_values(metric, ascending=True).head(n)
