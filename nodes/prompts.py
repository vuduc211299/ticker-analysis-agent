"""Prompt-loading helper used by all LLM-backed nodes."""

from __future__ import annotations

from config import PROMPTS_DIR


def load_prompt(name: str) -> str:
    """Load a prompt template from ``prompts/<name>.txt``."""
    path = PROMPTS_DIR / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(f"Prompt file not found: {path}")
