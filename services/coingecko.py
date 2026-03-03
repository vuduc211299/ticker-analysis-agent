"""CoinGecko Demo-API client with built-in rate-limit and retry logic."""

from __future__ import annotations

import logging
import re
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import COINGECKO_API_KEY, COINGECKO_BASE_URL
from indicators import (
    compute_ema,
    compute_fibonacci,
    compute_ma,
    compute_macd,
    compute_mfi,
    compute_obv,
    compute_ohlc_indicators,
    compute_rsi,
    compute_support_resistance,
    to_series,
)

log = logging.getLogger(__name__)

# ─── Resilient HTTP session ──────────────────────────────────────────────────

_RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)


def _build_session() -> requests.Session:
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=_RETRY_STRATEGY)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "accept": "application/json",
            "x-cg-demo-api-key": COINGECKO_API_KEY,
        }
    )
    return session


_session = _build_session()

# Minimum pause between CoinGecko calls (seconds).
_RATE_LIMIT_DELAY = 0.5


def _cg_get(endpoint: str, params: dict | None = None) -> Any:
    """Authenticated GET with automatic rate-limit spacing."""
    url = f"{COINGECKO_BASE_URL}{endpoint}"
    resp = _session.get(url, params=params or {}, timeout=30)
    resp.raise_for_status()
    time.sleep(_RATE_LIMIT_DELAY)
    return resp.json()


# ─── Coin-ID resolver ────────────────────────────────────────────────────────

_COMMON_MAP: dict[str, str] = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "SHIB": "shiba-inu",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "NEAR": "near",
    "ARB": "arbitrum",
    "OP": "optimism",
    "APT": "aptos",
    "SUI": "sui",
    "TRX": "tron",
    "FIL": "filecoin",
    "PEPE": "pepe",
    "WIF": "dogwifcoin",
}

_NAME_MAP: dict[str, str] = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binance coin": "BNB",
    "solana": "SOL",
    "ripple": "XRP",
    "dogecoin": "DOGE",
    "cardano": "ADA",
    "avalanche": "AVAX",
    "polkadot": "DOT",
    "polygon": "MATIC",
    "chainlink": "LINK",
    "uniswap": "UNI",
    "shiba inu": "SHIB",
    "litecoin": "LTC",
    "cosmos": "ATOM",
    "near": "NEAR",
    "arbitrum": "ARB",
    "optimism": "OP",
    "aptos": "APT",
    "sui": "SUI",
    "tron": "TRX",
    "filecoin": "FIL",
    "pepe": "PEPE",
    "dogwifcoin": "WIF",
}


def _normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


_NORMALIZED_NAME_MAP: dict[str, str] = {
    _normalized_key(name): ticker for name, ticker in _NAME_MAP.items()
}

_NORMALIZED_ID_MAP: dict[str, str] = {
    _normalized_key(coin_id): ticker for ticker, coin_id in _COMMON_MAP.items()
}


def get_supported_tickers() -> list[str]:
    """Return the highlighted/whitelisted ticker symbols."""
    return list(_COMMON_MAP.keys())


def is_supported_ticker(ticker: str) -> bool:
    """Check whether input maps to a highlighted symbol or full coin name."""
    return bool(normalize_supported_ticker(ticker))


def normalize_supported_ticker(value: str) -> str:
    """Normalize ticker-like input to a supported ticker symbol.

    Examples:
    - BTC -> BTC
    - bitcoin -> BTC
    - matic-network -> MATIC
    """
    raw = str(value or "").strip()
    if not raw:
        return ""

    upper = raw.upper()
    if upper in _COMMON_MAP:
        return upper

    key = _normalized_key(raw)
    if key in _NORMALIZED_NAME_MAP:
        return _NORMALIZED_NAME_MAP[key]
    if key in _NORMALIZED_ID_MAP:
        return _NORMALIZED_ID_MAP[key]

    return ""


def find_supported_ticker_in_text(text: str) -> str:
    """Best-effort extraction of a supported ticker/full-name from free text."""
    raw = str(text or "")
    if not raw:
        return ""

    token_candidates = re.findall(r"[A-Za-z0-9-]+", raw)
    for token in token_candidates:
        normalized = normalize_supported_ticker(token)
        if normalized:
            return normalized

    lower_text = raw.lower()
    for name, ticker in sorted(_NAME_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(name)}\b", lower_text):
            return ticker

    return ""


def resolve_coin_id(ticker: str) -> str:
    """Resolve a ticker symbol (e.g. ``BTC``) to a CoinGecko coin ID."""
    upper = str(ticker or "").upper()
    normalized_ticker = normalize_supported_ticker(ticker)
    if normalized_ticker in _COMMON_MAP:
        return _COMMON_MAP[normalized_ticker]

    try:
        data = _cg_get("/search", {"query": ticker})
        coins = data.get("coins", [])
        if coins:
            for coin in coins:
                if coin.get("symbol", "").upper() == upper:
                    return coin["id"]
            return coins[0]["id"]
    except Exception:
        log.warning("CoinGecko /search failed for %s — falling back to lower()", ticker)

    return upper.lower()


# ─── Individual data-fetch helpers ────────────────────────────────────────────


def fetch_price_data(coin_id: str) -> dict[str, Any]:
    """Current price, market cap, volume, 24 h change via ``/simple/price``."""
    try:
        data = _cg_get(
            "/simple/price",
            {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            },
        )
        return data.get(coin_id, {})
    except requests.RequestException as exc:
        log.error("fetch_price_data error: %s", exc)
        return {"error": str(exc)}


def fetch_coin_data(coin_id: str) -> dict[str, Any]:
    """Comprehensive coin metadata + market data via ``/coins/{id}``."""
    try:
        data = _cg_get(
            f"/coins/{coin_id}",
            {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "true",
                "developer_data": "false",
                "sparkline": "true",
            },
        )
        market = data.get("market_data", {})
        return {
            "name": data.get("name"),
            "symbol": data.get("symbol"),
            "market_cap_rank": data.get("market_cap_rank"),
            "current_price_usd": market.get("current_price", {}).get("usd"),
            "market_cap_usd": market.get("market_cap", {}).get("usd"),
            "total_volume_usd": market.get("total_volume", {}).get("usd"),
            "high_24h_usd": market.get("high_24h", {}).get("usd"),
            "low_24h_usd": market.get("low_24h", {}).get("usd"),
            "price_change_24h": market.get("price_change_24h"),
            "price_change_percentage_24h": market.get("price_change_percentage_24h"),
            "price_change_percentage_7d": market.get("price_change_percentage_7d"),
            "price_change_percentage_14d": market.get("price_change_percentage_14d"),
            "price_change_percentage_30d": market.get("price_change_percentage_30d"),
            "price_change_percentage_1y": market.get("price_change_percentage_1y"),
            "ath_usd": market.get("ath", {}).get("usd"),
            "ath_change_percentage": market.get("ath_change_percentage", {}).get("usd"),
            "atl_usd": market.get("atl", {}).get("usd"),
            "circulating_supply": market.get("circulating_supply"),
            "total_supply": market.get("total_supply"),
            "max_supply": market.get("max_supply"),
            "fully_diluted_valuation_usd": market.get("fully_diluted_valuation", {}).get("usd"),
            "sparkline_7d": market.get("sparkline_7d", {}).get("price", []),
            "sentiment_votes_up_percentage": data.get("sentiment_votes_up_percentage"),
            "sentiment_votes_down_percentage": data.get("sentiment_votes_down_percentage"),
            "community_data": data.get("community_data", {}),
        }
    except requests.RequestException as exc:
        log.error("fetch_coin_data error: %s", exc)
        return {"error": str(exc)}


def fetch_market_chart(coin_id: str, days: int | str) -> dict[str, Any]:
    """Historical prices, market_caps, total_volumes via ``/coins/{id}/market_chart``."""
    try:
        return _cg_get(
            f"/coins/{coin_id}/market_chart",
            {"vs_currency": "usd", "days": str(days)},
        )
    except requests.RequestException as exc:
        log.error("fetch_market_chart error: %s", exc)
        return {"error": str(exc)}


def fetch_ohlc(coin_id: str, days: int | str) -> list[list]:
    """OHLC candle data via ``/coins/{id}/ohlc``."""
    try:
        data = _cg_get(
            f"/coins/{coin_id}/ohlc",
            {"vs_currency": "usd", "days": str(days)},
        )
        return data if isinstance(data, list) else []
    except requests.RequestException as exc:
        log.error("fetch_ohlc error: %s", exc)
        return []


# ─── Orchestrator ─────────────────────────────────────────────────────────────


def fetch_all_data(coin_id: str) -> dict[str, Any]:
    """Fetch all CoinGecko data and compute technical indicators.

    Returns a comprehensive dict ready for analysis.
    """
    result: dict[str, Any] = {"coin_id": coin_id, "errors": []}

    # 1) Current price snapshot
    result["price_data"] = fetch_price_data(coin_id)

    # 2) Full coin metadata + market data
    result["coin_data"] = fetch_coin_data(coin_id)

    # 3) Market charts — multiple timeframes
    chart_1d = fetch_market_chart(coin_id, 1)
    chart_7d = fetch_market_chart(coin_id, 7)
    chart_30d = fetch_market_chart(coin_id, 30)

    result["charts"] = {
        "1d": {
            "prices_count": len(chart_1d.get("prices", [])),
            "latest_prices": (chart_1d.get("prices") or [])[-10:],
        },
        "7d": {"prices_count": len(chart_7d.get("prices", []))},
        "30d": {"prices_count": len(chart_30d.get("prices", []))},
    }

    # 4) OHLC candles
    ohlc_1d = fetch_ohlc(coin_id, 1)
    ohlc_7d = fetch_ohlc(coin_id, 7)
    ohlc_30d = fetch_ohlc(coin_id, 30)

    result["ohlc"] = {
        "1d_candles": {
            "data": ohlc_1d,
            "indicators": compute_ohlc_indicators(ohlc_1d),
        },
        "7d_candles": {
            "data": ohlc_7d[-20:],
            "indicators": compute_ohlc_indicators(ohlc_7d),
        },
        "30d_candles": {
            "data": ohlc_30d[-20:],
            "indicators": compute_ohlc_indicators(ohlc_30d),
        },
    }

    # 5) Technical indicators from 30-day chart
    prices_30d = to_series(chart_30d.get("prices", []))
    volumes_30d = to_series(chart_30d.get("total_volumes", []))

    indicators: dict[str, Any] = {}
    if len(prices_30d) > 0:
        indicators["moving_averages"] = compute_ma(prices_30d)
        indicators["exponential_moving_averages"] = compute_ema(prices_30d)
        indicators["RSI_14"] = compute_rsi(prices_30d)
        indicators["MACD"] = compute_macd(prices_30d)
        indicators["support_resistance"] = compute_support_resistance(prices_30d)

        recent_high = float(prices_30d.max())
        recent_low = float(prices_30d.min())
        indicators["fibonacci_30d"] = compute_fibonacci(recent_high, recent_low)

    if len(volumes_30d) > 0 and len(prices_30d) > 0:
        indicators["OBV"] = compute_obv(prices_30d, volumes_30d)
        indicators["MFI_14"] = compute_mfi(prices_30d, volumes_30d)

    result["technical_indicators"] = indicators
    return result
