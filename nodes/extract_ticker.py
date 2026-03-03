"""Node 1 — Use Gemini to extract a ticker symbol and resolve it to a CoinGecko ID."""

from __future__ import annotations

import json
import logging
import re

from nodes.state import AgentState
from nodes.prompts import load_prompt
from services.coingecko import (
    find_supported_ticker_in_text,
    get_supported_tickers,
    normalize_supported_ticker,
    resolve_coin_id,
)
from services.llm import call_llm

log = logging.getLogger(__name__)


def extract_ticker(state: AgentState) -> AgentState:
    raw_input = state.get("user_input", "")
    errors: list[str] = list(state.get("errors", []))
    ticker = ""

    direct_ticker = find_supported_ticker_in_text(raw_input)
    if direct_ticker:
        ticker = direct_ticker

    if not ticker:
        system_prompt = load_prompt("extract_ticker")
        user_prompt = f"User input: {raw_input}"

        try:
            llm_output = call_llm(system_prompt, user_prompt)
            log.info("LLM output: %s", llm_output)

            match = re.search(r"\{.*\}", llm_output, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                candidate = str(parsed.get("ticker", "")).strip()
                normalized = normalize_supported_ticker(candidate)
                if normalized:
                    ticker = normalized
                else:
                    errors.append("LLM returned invalid ticker.")
            else:
                errors.append("LLM ticker output was not JSON.")
        except Exception as exc:
            errors.append(f"Ticker extraction LLM error: {exc}.")

    if not ticker:
        allowed = ", ".join(get_supported_tickers())
        message = (
            "Sorry, I can't help you analysis requested coin. "
            "Please ask only the coin in list bellow\n"
            f"{allowed}"
        )
        errors.append(f"Unsupported ticker requested: {ticker}")
        return {
            "ticker": ticker,
            "coin_id": "",
            "report": message,
            "errors": errors,
        }

    coin_id = resolve_coin_id(ticker)
    log.info("Ticker: %s → CoinGecko ID: %s", ticker, coin_id)

    return {"ticker": ticker, "coin_id": coin_id, "errors": errors}
