"""Shared helpers for indicator computation."""

from __future__ import annotations

import pandas as pd


def to_series(prices: list) -> pd.Series:
    """Convert a list of [timestamp, value] pairs (or plain values) to a pandas Series."""
    if not prices:
        return pd.Series(dtype=float)
    if isinstance(prices[0], (list, tuple)):
        return pd.Series([p[1] for p in prices], dtype=float)
    return pd.Series(prices, dtype=float)
