"""Price-level indicators: Fibonacci retracement, support / resistance."""

from __future__ import annotations

import pandas as pd


def compute_fibonacci(high: float, low: float) -> dict[str, float]:
    """Compute Fibonacci retracement levels from a high/low range."""
    diff = high - low
    return {
        "fib_0.0 (Low)": round(low, 4),
        "fib_0.236": round(low + 0.236 * diff, 4),
        "fib_0.382": round(low + 0.382 * diff, 4),
        "fib_0.5": round(low + 0.5 * diff, 4),
        "fib_0.618": round(low + 0.618 * diff, 4),
        "fib_0.786": round(low + 0.786 * diff, 4),
        "fib_1.0 (High)": round(high, 4),
    }


def compute_support_resistance(
    prices: pd.Series,
    window: int = 5,
) -> dict[str, list[float]]:
    """Detect approximate support and resistance via local minima / maxima."""
    if len(prices) < window * 2 + 1:
        return {"support_levels": [], "resistance_levels": []}

    supports: list[float] = []
    resistances: list[float] = []
    arr = prices.values

    for i in range(window, len(arr) - window):
        is_min = all(arr[i] <= arr[i - j] for j in range(1, window + 1)) and all(
            arr[i] <= arr[i + j] for j in range(1, window + 1)
        )
        is_max = all(arr[i] >= arr[i - j] for j in range(1, window + 1)) and all(
            arr[i] >= arr[i + j] for j in range(1, window + 1)
        )
        if is_min:
            supports.append(round(float(arr[i]), 4))
        if is_max:
            resistances.append(round(float(arr[i]), 4))

    def _dedup(levels: list[float], threshold: float = 0.005) -> list[float]:
        if not levels:
            return []
        sorted_lvls = sorted(levels)
        result = [sorted_lvls[0]]
        for lvl in sorted_lvls[1:]:
            if abs(lvl - result[-1]) / result[-1] > threshold:
                result.append(lvl)
        return result[-5:]

    return {
        "support_levels": _dedup(supports),
        "resistance_levels": _dedup(resistances),
    }
