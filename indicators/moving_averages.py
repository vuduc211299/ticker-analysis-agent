"""Simple & Exponential Moving Averages."""

from __future__ import annotations

import pandas as pd


def compute_ma(
    prices: pd.Series,
    windows: list[int] | None = None,
) -> dict[str, float | None]:
    """Compute Simple Moving Averages for the given *windows*."""
    windows = windows or [7, 14, 25, 50, 99, 200]
    result: dict[str, float | None] = {}
    for w in windows:
        if len(prices) >= w:
            result[f"MA_{w}"] = round(float(prices.rolling(w).mean().iloc[-1]), 4)
        else:
            result[f"MA_{w}"] = None
    return result


def compute_ema(
    prices: pd.Series,
    spans: list[int] | None = None,
) -> dict[str, float | None]:
    """Compute Exponential Moving Averages for the given *spans*."""
    spans = spans or [12, 26, 50, 200]
    result: dict[str, float | None] = {}
    for s in spans:
        if len(prices) >= s:
            result[f"EMA_{s}"] = round(
                float(prices.ewm(span=s, adjust=False).mean().iloc[-1]), 4
            )
        else:
            result[f"EMA_{s}"] = None
    return result
