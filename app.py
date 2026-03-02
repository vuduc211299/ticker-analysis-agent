from __future__ import annotations

from fastapi import FastAPI

from api.routes import chart_router, report_router

app = FastAPI(
    title="Crypto Analysis API",
    version="1.0.0",
    description=(
        "API for coin chart data and AI-generated structured ticker reports. "
        "Only supported tickers are allowed."
    ),
)

app.include_router(chart_router)
app.include_router(report_router)
