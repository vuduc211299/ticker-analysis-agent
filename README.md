# Crypto Analysis API

Crypto Analysis API is a FastAPI service that turns natural-language crypto questions into structured market reports and chart-ready price series. It combines market data from trusted sources (e.g Coingekco), technical indicators, and a LLM model to produce concise analysis for supported coins.

## Overview

This app is built around a small agent workflow:

1. Extract a supported ticker from the user's request.
2. Resolve the ticker to a CoinGecko coin ID.
3. Fetch live market data and historical price data.
4. Compute technical indicators.
5. Use a local LLM to generate analysis and a formatted markdown report.

The current default model is `qwen2.5:3b` served locally with Ollama.

## Capabilities

- Natural-language crypto query handling
- Supported-ticker validation and normalization
- CoinGecko market data retrieval
- Technical analysis signal generation, including:
  - moving averages and EMA
  - RSI, MACD, and MFI
  - OBV
  - support/resistance and Fibonacci levels
  - OHLC-derived indicator summaries
- AI-generated markdown reports with structured sections
- Chart data generation for multiple timeframes
- FastAPI-based JSON endpoints for frontend or agent integration

## API Endpoints

### POST /api/v1/report

Generates a structured AI report from a natural-language request.

Example request body:

```json
{
  "query": "Give me a short-term outlook for BTC"
}
```

Returns:

- normalized `ticker`
- resolved `coin_id`
- full `report_markdown`
- parsed report `sections`
- intermediate `analysis`
- collected `errors`

### POST /api/v1/chart-data

Builds chart-ready historical price series from a natural-language request.

Example request body:

```json
{
  "query": "Show me the chart data for ETH"
}
```

Returns time-series data for these views:

- `15m`
- `1h`
- `4h`
- `1D`
- `1W`

## Main Components

- `app.py` — FastAPI app entry point
- `agents.py` — LangGraph workflow orchestration
- `nodes/` — workflow steps for extraction, data fetch, analysis, and reporting
- `services/coingecko.py` — CoinGecko client and indicator orchestration
- `services/llm.py` — local Ollama LLM wrapper
- `services/chart_service.py` — chart data shaping and resampling
- `services/report_service.py` — markdown section extraction
- `indicators/` — pure technical-analysis computations
- `schemas/` — request and response models

## Runtime Dependencies

- FastAPI for the API layer
- CoinGecko Demo API for market data
- Ollama for local model inference
- `qwen2.5:3b` as the default local model
- LangGraph for workflow orchestration

## Quick Start

1. Install Python dependencies.
2. Make sure Ollama is running locally.
3. Pull or confirm the `qwen2.5:3b` model is available.
4. Set values in `.env`.
5. Start the API with Uvicorn.

Default LLM-related environment settings:

```env
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=qwen2.5:3b
```

## Notes

- The service only supports a curated list of tickers.
- If report generation fails, the app returns a fallback minimal report.
- The OpenAPI schema is available in [openapi.json](openapi.json).
