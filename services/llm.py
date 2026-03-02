"""Thin wrapper around the Google Gemini generative-AI client."""

from __future__ import annotations

import logging

from google import genai

from config import LLM_API_KEY, LLM_MODEL

log = logging.getLogger(__name__)

# ─── Singleton client ─────────────────────────────────────────────────────────
_client: genai.Client | None = None


def _get_client(api_key: str | None = None) -> genai.Client:
    global _client
    key = api_key or LLM_API_KEY
    if _client is None:
        _client = genai.Client(api_key=key)
    return _client


def call_llm(
    system_prompt: str,
    user_prompt: str,
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> str:
    """Send a prompt to Gemini and return the text response.

    Raises ``RuntimeError`` when the model returns no text.
    """
    client = _get_client(api_key)
    combined = f"System instruction:\n{system_prompt}\n\nUser input:\n{user_prompt}"
    response = client.models.generate_content(
        model=model or LLM_MODEL,
        contents=combined,
    )

    text = getattr(response, "text", None)
    if text and text.strip():
        return text.strip()

    raise RuntimeError("Gemini response did not contain text output.")
