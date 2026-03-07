from __future__ import annotations

from fastapi import APIRouter

from schemas.chart import ChartDataResponse, ChartRequest
from services.api_errors import raise_unsupported_ticker
from services.chart_service import (extract_ticker_from_query,
                                    get_chart_series_for_views)
from services.coingecko import is_supported_ticker, resolve_coin_id

router = APIRouter()


@router.post("/api/v1/chart-data", response_model=ChartDataResponse)
def get_chart_data(payload: ChartRequest) -> ChartDataResponse:
    normalized_ticker = extract_ticker_from_query(payload.query)

    if not is_supported_ticker(normalized_ticker):
        raise_unsupported_ticker(normalized_ticker)

    coin_id = resolve_coin_id(normalized_ticker)
    series = get_chart_series_for_views(coin_id)

    return ChartDataResponse(
        query=payload.query,
        ticker=normalized_ticker,
        coin_id=coin_id,
        series=series,
    )
