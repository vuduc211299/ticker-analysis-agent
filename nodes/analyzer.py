"""Node 3 — Gemini-powered market-data analysis."""

from __future__ import annotations

import json
import logging
from typing import Any

from nodes.state import AgentState
from nodes.prompts import load_prompt
from services.llm import call_llm

log = logging.getLogger(__name__)


def analyzer_node(state: AgentState) -> AgentState:
    if state.get("report"):
        return {}

    ticker = state.get("ticker", "UNKNOWN")
    coin_id = state.get("coin_id", "unknown")
    api_data = state.get("api_data") or {}
    errors: list[str] = list(state.get("errors", []))

    log.info("Analysing %s (%s) …", ticker, coin_id)

    system_prompt = load_prompt("analyzer")
    data_summary = _prepare_analysis_payload(api_data, ticker)

    user_prompt = (
        f"Ticker: {ticker} (CoinGecko ID: {coin_id})\n\n"
        f"Market Data & Technical Indicators:\n{json.dumps(data_summary, indent=2, default=str)}\n\n"
        f"Errors/Warnings: {json.dumps(errors, ensure_ascii=False)}\n\n"
        "Please provide your full analysis now."
    )

    try:
        analysis = call_llm(system_prompt, user_prompt)
        log.info("Analysis complete (%d chars)", len(analysis))
    except Exception as exc:
        analysis = (
            f"## Analysis for {ticker}\n\n"
            f"Analysis generation failed: {exc}\n\n"
            "Unable to produce automated analysis. Please review raw data manually."
        )
        errors.append(f"Analyzer LLM error: {exc}")

    return {"analysis": analysis, "errors": errors}


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _prepare_analysis_payload(api_data: dict, ticker: str) -> dict[str, Any]:
    """Extract the most relevant data points for the LLM analysis prompt."""
    payload: dict[str, Any] = {"ticker": ticker}

    # Price data
    price = api_data.get("price_data", {})
    if price and "error" not in price:
        payload["current_price"] = {
            "usd": price.get("usd"),
            "market_cap": price.get("usd_market_cap"),
            "volume_24h": price.get("usd_24h_vol"),
            "change_24h_pct": price.get("usd_24h_change"),
        }

    # Coin data
    coin = api_data.get("coin_data", {})
    if coin and "error" not in coin:
        payload["market_overview"] = {
            "name": coin.get("name"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "high_24h": coin.get("high_24h_usd"),
            "low_24h": coin.get("low_24h_usd"),
            "price_change_7d_pct": coin.get("price_change_percentage_7d"),
            "price_change_14d_pct": coin.get("price_change_percentage_14d"),
            "price_change_30d_pct": coin.get("price_change_percentage_30d"),
            "ath": coin.get("ath_usd"),
            "ath_change_pct": coin.get("ath_change_percentage"),
            "circulating_supply": coin.get("circulating_supply"),
            "max_supply": coin.get("max_supply"),
            "sentiment_up_pct": coin.get("sentiment_votes_up_percentage"),
            "sentiment_down_pct": coin.get("sentiment_votes_down_percentage"),
        }

    # Technical indicators
    indicators = api_data.get("technical_indicators", {})
    if indicators:
        payload["technical_indicators"] = indicators

    # OHLC candle summaries
    ohlc = api_data.get("ohlc", {})
    for tf_key in ("1d_candles", "7d_candles", "30d_candles"):
        tf_indicators = ohlc.get(tf_key, {}).get("indicators", {})
        if tf_indicators:
            payload[f"ohlc_{tf_key}"] = tf_indicators

    return payload
