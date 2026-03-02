"""Centralised configuration — loads secrets from environment / .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (no-op if the file is absent)
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)

# ─── LLM (Google Gemini) ─────────────────────────────────────────────────────
LLM_API_KEY: str = os.environ.get("LLM_API_KEY", "")
LLM_MODEL: str = os.environ.get("LLM_MODEL", "gemini-3-flash-preview")

# ─── CoinGecko ───────────────────────────────────────────────────────────────
COINGECKO_API_KEY: str = os.environ.get("COINGECKO_API_KEY", "")
COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT: Path = Path(__file__).resolve().parent
SKILLS_DIR: Path = PROJECT_ROOT / "skills"
PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"
