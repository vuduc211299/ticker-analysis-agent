from __future__ import annotations

from fastapi import APIRouter, HTTPException

from agents import run_agent
from schemas.report import ReportRequest, ReportResponse
from services.api_errors import raise_unsupported_ticker
from services.coingecko import is_supported_ticker
from services.report_service import extract_report_sections

router = APIRouter()


@router.post("/api/v1/report", response_model=ReportResponse)
def get_structured_report(payload: ReportRequest) -> ReportResponse:
    state = run_agent(payload.query)

    ticker = str(state.get("ticker", "")).upper()
    errors = list(state.get("errors", []))
    report = str(state.get("report", ""))

    if ticker and not is_supported_ticker(ticker):
        raise_unsupported_ticker(ticker)

    if not report:
        raise HTTPException(
            status_code=502,
            detail={"message": "Report generation failed. Empty report output."},
        )

    coin_id = str(state.get("coin_id", ""))
    analysis = str(state.get("analysis", ""))
    sections = extract_report_sections(report)

    return ReportResponse(
        ticker=ticker,
        coin_id=coin_id,
        report_markdown=report,
        sections=sections,
        analysis=analysis,
        errors=errors,
    )
