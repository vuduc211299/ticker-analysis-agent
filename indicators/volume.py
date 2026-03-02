"""Volume-based indicators: OBV."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_obv(prices: pd.Series, volumes: pd.Series) -> float | None:
    """Compute On-Balance Volume."""
    if len(prices) < 2 or len(volumes) < 2:
        return None
    min_len = min(len(prices), len(volumes))
    p = prices.iloc[-min_len:].reset_index(drop=True)
    v = volumes.iloc[-min_len:].reset_index(drop=True)
    direction = pd.Series(
        np.where(p.diff() > 0, 1, np.where(p.diff() < 0, -1, 0)),
        dtype=float,
    )
    direction.iloc[0] = 0
    obv = (direction * v).cumsum()
    return round(float(obv.iloc[-1]), 2)
