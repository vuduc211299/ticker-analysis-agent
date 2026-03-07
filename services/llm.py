"""Thin wrapper around the local Ollama chat API."""

from __future__ import annotations

import logging

import requests

from config import LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT_SECONDS

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
        timeout=LLM_TIMEOUT_SECONDS,
    )
    if response.status_code == 404:
        detail = _build_model_not_found_detail(model or LLM_MODEL)
        raise RuntimeError(detail)

    response.raise_for_status()

    payload = response.json()
    text = ((payload.get("message") or {}).get("content") if isinstance(payload, dict) else None)
    if text and text.strip():
        return text.strip()

    error = payload.get("error") if isinstance(payload, dict) else None
    if error:
        raise RuntimeError(f"Ollama request failed: {error}")

    raise RuntimeError("Ollama response did not contain text output.")


def _build_model_not_found_detail(requested_model: str) -> str:
    available_models: list[str] = []
    try:
        tags = requests.get(f"{LLM_BASE_URL.rstrip('/')}/api/tags", timeout=10)
        tags.raise_for_status()
        payload = tags.json()
        models = payload.get("models", []) if isinstance(payload, dict) else []
        for model in models:
            if isinstance(model, dict) and isinstance(model.get("name"), str):
                available_models.append(model["name"])
    except Exception:
        available_models = []

    if available_models:
        available = ", ".join(sorted(set(available_models)))
        return (
            f"Ollama model '{requested_model}' not found. "
            f"Available local models: {available}. "
            "Set LLM_MODEL to one of the available models or pull the missing model."
        )

    return (
        f"Ollama model '{requested_model}' not found. "
        "Set LLM_MODEL to an installed model or pull the missing model with ollama pull."
    )
