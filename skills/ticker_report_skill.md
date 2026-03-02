# Ticker Analysis Report Skill

## Goal

Create a comprehensive, decision-ready analysis report about one cryptocurrency ticker based on real market data, technical indicators, and AI-generated analysis.

## Required Output Format

Use exactly these sections in this order:

1. `# Ticker Report: <TICKER>`
2. `## Executive Summary` (3-5 bullets: current price, 24h change, overall sentiment, key recommendation)
3. `## Market Overview` (current price, market cap, rank, 24h high/low, volume, supply data)
4. `## Technical Analysis`
   - Moving Averages (MA & EMA — state whether price is above/below key MAs)
   - RSI (value + interpretation: oversold <30, neutral 30-70, overbought >70)
   - MACD (line, signal, histogram — bullish/bearish crossover status)
   - Volume Indicators (OBV trend, MFI value + interpretation)
5. `## Price Action & Levels`
   - Fibonacci retracement levels
   - Support levels
   - Resistance levels
   - Recent OHLC candle summary
6. `## Sentiment Snapshot` (API community sentiment if available, analyst sentiment)
7. `## Recommendation` (STRONG BUY / BUY / DCA / HOLD / SELL / STRONG SELL — with reasoning)
8. `## Risks / Unknowns` (3-5 bullets)
9. `## Next Watch Items (24-72h)` (3-5 bullets with specific price levels or events)

## Writing Rules

- Keep it concise and factual.
- Do not invent facts not present in API data or analyst assessment.
- Mention when data is missing, blocked, or errored.
- Prefer plain English, no hype language.
- Include specific numbers from the data (prices, percentages, indicator values).
- Clearly separate data-driven observations from analyst opinions.
