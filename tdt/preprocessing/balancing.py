"""Class-aware sampling diagnostics."""

from __future__ import annotations

import pandas as pd


def inverse_frequency_weights(distribution: pd.DataFrame, count_column: str = "pixel_count") -> pd.DataFrame:
    """Compute normalized inverse-frequency class weights."""

    frame = distribution.copy()
    counts = frame[count_column].clip(lower=1)
    weights = 1.0 / counts
    frame["weight"] = weights / weights.mean()
    return frame
