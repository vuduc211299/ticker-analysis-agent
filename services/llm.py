"""Thin wrapper around the local Ollama chat API."""

from __future__ import annotations

import logging

import requests

from config import LLM_BASE_URL, LLM_MODEL

log = logging.getLogger(__name__)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
) -> str:
    """Send a prompt to Ollama and return the text response.

    Raises ``RuntimeError`` when the model returns no text.
    """
    response = requests.post(
        f"{LLM_BASE_URL.rstrip('/')}/api/chat",
        json={
            "model": model or LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()

    payload = response.json()
    text = ((payload.get("message") or {}).get("content") if isinstance(payload, dict) else None)
    if text and text.strip():
        return text.strip()

    error = payload.get("error") if isinstance(payload, dict) else None
    if error:
        raise RuntimeError(f"Ollama request failed: {error}")

    raise RuntimeError("Ollama response did not contain text output.")
