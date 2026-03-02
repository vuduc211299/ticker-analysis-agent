"""Indicators computed from OHLC candle data."""

from __future__ import annotations

from typing import Any

import pandas as pd

from indicators.levels import compute_fibonacci
from indicators.oscillators import compute_macd, compute_rsi


def compute_ohlc_indicators(ohlc_data: list[list]) -> dict[str, Any]:
    """Compute indicators specifically from OHLC candle data."""
    if not ohlc_data or len(ohlc_data) < 2:
        return {}

    df = pd.DataFrame(ohlc_data, columns=["timestamp", "open", "high", "low", "close"])
    closes = df["close"]
    highs = df["high"]
    lows = df["low"]

    recent_high = float(highs.max())
    recent_low = float(lows.min())

    return {
        "candle_count": len(df),
        "period_high": round(recent_high, 4),
        "period_low": round(recent_low, 4),
        "latest_open": round(float(df["open"].iloc[-1]), 4),
        "latest_close": round(float(df["close"].iloc[-1]), 4),
        "latest_high": round(float(df["high"].iloc[-1]), 4),
        "latest_low": round(float(df["low"].iloc[-1]), 4),
        "fibonacci": compute_fibonacci(recent_high, recent_low),
        "rsi_from_candles": compute_rsi(closes),
        "macd_from_candles": compute_macd(closes),
    }
