from __future__ import annotations

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language user request")


class ReportSection(BaseModel):
    title: str
    content: str


class ReportResponse(BaseModel):
    ticker: str
    coin_id: str
    report_markdown: str
    sections: list[ReportSection]
    analysis: str
    errors: list[str]
