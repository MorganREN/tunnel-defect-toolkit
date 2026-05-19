"""Confusion analysis helpers."""

from __future__ import annotations

import pandas as pd


def confusion_to_dataframe(matrix, class_names: dict[int, str]) -> pd.DataFrame:
    """Convert a confusion matrix to a labeled DataFrame."""

    labels = [class_names.get(i, str(i)) for i in range(matrix.shape[0])]
    return pd.DataFrame(matrix, index=labels, columns=labels)
