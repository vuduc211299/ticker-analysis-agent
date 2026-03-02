"""Node 2 — Fetch real market data from CoinGecko and compute technical indicators."""

from __future__ import annotations

import logging

from nodes.state import AgentState
from services.coingecko import fetch_all_data

log = logging.getLogger(__name__)


def fetch_api_data(state: AgentState) -> AgentState:
    if state.get("report"):
        return {}

    coin_id = state.get("coin_id", "")
    errors: list[str] = list(state.get("errors", []))

    if not coin_id:
        errors.append("No valid coin_id to fetch.")
        return {"api_data": {}, "errors": errors}

    log.info("Fetching data for coin ID: %s …", coin_id)

    try:
        api_data = fetch_all_data(coin_id)
        api_errors = api_data.pop("errors", [])
        errors.extend(api_errors)
        log.info("Fetched data — keys: %s", list(api_data.keys()))
    except Exception as exc:
        api_data = {"error": str(exc)}
        errors.append(f"API fetch error: {exc}")
        log.error("Fetch failed: %s", exc)

    return {"api_data": api_data, "errors": errors}
