from __future__ import annotations

from pydantic import BaseModel, Field


class ChartPoint(BaseModel):
    timestamp_ms: int
    price_usd: float


class ChartSeries(BaseModel):
    timeframe: str
    points: list[ChartPoint]


class ChartRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language user request")


class ChartDataResponse(BaseModel):
    query: str
    ticker: str
    coin_id: str
    series: dict[str, ChartSeries]
