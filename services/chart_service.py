from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from schemas.chart import ChartPoint, ChartSeries
from services.coingecko import fetch_market_chart, find_supported_ticker_in_text


def extract_ticker_from_query(query: str) -> str:
    return find_supported_ticker_in_text(query)


def to_points(raw_prices: list[Any]) -> list[ChartPoint]:
    return [
        ChartPoint(timestamp_ms=int(item[0]), price_usd=float(item[1]))
        for item in raw_prices
        if isinstance(item, (list, tuple)) and len(item) >= 2
    ]


def resample_series(points: list[ChartPoint], bucket_ms: int) -> list[ChartPoint]:
    if not points:
        return []

    sampled: list[ChartPoint] = []
    current_bucket = points[0].timestamp_ms // bucket_ms
    last_point = points[0]

    for point in points[1:]:
        point_bucket = point.timestamp_ms // bucket_ms
        if point_bucket != current_bucket:
            sampled.append(last_point)
            current_bucket = point_bucket
        last_point = point

    sampled.append(last_point)
    return sampled


def get_chart_series_for_views(coin_id: str) -> dict[str, ChartSeries]:
    one_day = fetch_market_chart(coin_id, 1)
    seven_day = fetch_market_chart(coin_id, 7)
    one_year = fetch_market_chart(coin_id, 365)

    for payload in (one_day, seven_day, one_year):
        if "error" in payload:
            raise HTTPException(status_code=502, detail={"message": payload["error"]})

    points_1d = to_points(one_day.get("prices", []))
    points_7d = to_points(seven_day.get("prices", []))
    points_1y = to_points(one_year.get("prices", []))

    return {
        "15m": ChartSeries(timeframe="15m", points=resample_series(points_1d, 15 * 60 * 1000)),
        "1h": ChartSeries(timeframe="1h", points=resample_series(points_1d, 60 * 60 * 1000)),
        "4h": ChartSeries(timeframe="4h", points=resample_series(points_7d, 4 * 60 * 60 * 1000)),
        "1D": ChartSeries(timeframe="1D", points=resample_series(points_1y, 24 * 60 * 60 * 1000)),
        "1W": ChartSeries(timeframe="1W", points=resample_series(points_1y, 7 * 24 * 60 * 60 * 1000)),
    }
