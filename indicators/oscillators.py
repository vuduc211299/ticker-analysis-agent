"""Oscillator indicators: RSI, MACD, MFI."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_rsi(prices: pd.Series, period: int = 14) -> float | None:
    """Compute *period*-RSI using Wilder's smoothing."""
    if len(prices) < period + 1:
        return None
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)


def compute_macd(prices: pd.Series) -> dict[str, float | None]:
    """Compute MACD (12, 26, 9) — line, signal, histogram."""
    if len(prices) < 26:
        return {"MACD_line": None, "MACD_signal": None, "MACD_histogram": None}
    ema12 = prices.ewm(span=12, adjust=False).mean()
    ema26 = prices.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal
    return {
        "MACD_line": round(float(macd_line.iloc[-1]), 4),
        "MACD_signal": round(float(signal.iloc[-1]), 4),
        "MACD_histogram": round(float(histogram.iloc[-1]), 4),
    }


def compute_mfi(
    prices: pd.Series,
    volumes: pd.Series,
    period: int = 14,
) -> float | None:
    """Compute Money Flow Index (approximation using price as typical price)."""
    if len(prices) < period + 1 or len(volumes) < period + 1:
        return None
    min_len = min(len(prices), len(volumes))
    p = prices.iloc[-min_len:].reset_index(drop=True)
    v = volumes.iloc[-min_len:].reset_index(drop=True)

    money_flow = p * v
    delta = p.diff()
    pos_flow = pd.Series(np.where(delta > 0, money_flow, 0), dtype=float)
    neg_flow = pd.Series(np.where(delta < 0, money_flow, 0), dtype=float)
    pos_sum = pos_flow.rolling(period).sum()
    neg_sum = neg_flow.rolling(period).sum()
    mfr = pos_sum / neg_sum.replace(0, np.nan)
    mfi_val = 100 - (100 / (1 + mfr))
    val = mfi_val.iloc[-1]
    return round(float(val), 2) if pd.notna(val) else None
