"""Node 4 — Build the final Markdown report using the skill template."""

from __future__ import annotations

import json
import logging

from config import SKILLS_DIR
from nodes.prompts import load_prompt
from nodes.state import AgentState
from services.llm import call_llm

log = logging.getLogger(__name__)

_SKILL_PATH = SKILLS_DIR / "ticker_report_skill.md"


def reporter_node(state: AgentState) -> AgentState:
    if state.get("report"):
        return {}

    errors: list[str] = list(state.get("errors", []))

    if _SKILL_PATH.exists():
        skill_text = _SKILL_PATH.read_text(encoding="utf-8")
    else:
        skill_text = ""
        errors.append(f"Skill file not found: {_SKILL_PATH.name}")

    report = _render_report(state, skill_text)
    return {"report": report, "errors": errors}


def _render_report(state: AgentState, skill_text: str) -> str:
    ticker = state.get("ticker", "UNKNOWN")
    coin_id = state.get("coin_id", "unknown")
    analysis = state.get("analysis", "No analysis available.")
    api_data = state.get("api_data") or {}
    errors = state.get("errors", [])

    price = api_data.get("price_data", {})
    coin = api_data.get("coin_data", {})
    indicators = api_data.get("technical_indicators", {})

    system_prompt = load_prompt("reporter")
    user_prompt = (
        f"Ticker: {ticker} (CoinGecko ID: {coin_id})\n\n"
        "## Skill Instructions (follow this format):\n"
        f"{skill_text}\n\n"
        "## Analyst's Assessment:\n"
        f"{analysis}\n\n"
        "## Key Data Points:\n"
        f"Price data: {json.dumps(price, default=str)}\n"
        f"Coin data: {json.dumps({k: v for k, v in coin.items() if k != 'sparkline_7d'}, default=str)}\n"
        f"Technical indicators: {json.dumps(indicators, default=str)}\n"
        f"Errors: {json.dumps(errors, ensure_ascii=False)}\n\n"
        "Now write the complete report following the skill template."
    )

    try:
        return call_llm(system_prompt, user_prompt)
    except Exception as exc:
        log.error("Report generation failed: %s", exc)
        return (
            f"# Ticker Report: {ticker}\n\n"
            "## Executive Summary\n"
            f"- Report generation failed: {exc}\n"
            "- Using fallback minimal output.\n\n"
            "## Analyst Assessment\n"
            f"{analysis}\n\n"
            "## Sentiment Snapshot\n"
            "- Not available due to report generation failure.\n\n"
            "## Risks / Unknowns\n"
            "- LLM report generation failed.\n\n"
            "## Next Watch Items (24-72h)\n"
            "- Retry with valid API key/model."
        )
