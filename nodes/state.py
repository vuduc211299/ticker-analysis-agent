"""Shared pipeline state definition."""

from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    user_input: str
    ticker: str
    coin_id: str
    api_data: dict[str, Any] | None
    analysis: str
    errors: list[str]
    report: str
