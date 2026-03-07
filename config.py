"""Centralised configuration — loads secrets from environment / .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (no-op if the file is absent)
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)


def _get_int_env(name: str, default: int) -> int:
	value = os.environ.get(name)
	if value is None or not value.strip():
		return default
	try:
		return int(value)
	except ValueError:
		return default

# ─── LLM (Ollama) ────────────────────────────────────────────────────────────
LLM_BASE_URL: str = os.environ.get("LLM_BASE_URL", "http://localhost:11434")
LLM_MODEL: str = os.environ.get("LLM_MODEL", "qwen2.5:3b")
LLM_TIMEOUT_SECONDS: int = _get_int_env("LLM_TIMEOUT_SECONDS", 360)

# ─── CoinGecko ───────────────────────────────────────────────────────────────
COINGECKO_API_KEY: str = os.environ.get("COINGECKO_API_KEY", "")
COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT: Path = Path(__file__).resolve().parent
SKILLS_DIR: Path = PROJECT_ROOT / "skills"
PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"
