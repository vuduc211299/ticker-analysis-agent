from __future__ import annotations

from fastapi import HTTPException

from services.coingecko import get_supported_tickers


def raise_unsupported_ticker(ticker: str) -> None:
    supported = get_supported_tickers()
    raise HTTPException(
        status_code=400,
        detail={
            "message": (
                "Sorry, I can't help you analysis requested coin. "
                "Please ask only the coin in list bellow"
            ),
            "ticker": ticker.upper(),
            "supported_tickers": supported,
        },
    )
