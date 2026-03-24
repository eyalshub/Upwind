# iam_policy_classifier/providers/ollama_provider.py
from __future__ import annotations

import requests
from typing import Optional

from iam_policy_classifier.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Ollama implementation of the LLMProvider interface.

    This provider uses Ollama's local HTTP API for single-shot
    prompt completion.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = 180,
    ):
        """
        Initialize the Ollama provider.

        Args:
            base_url: Ollama server base URL.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(
        self,
        *,
        prompt: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        """
        Execute a single-shot completion using Ollama.
        """
        endpoint = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }

        response = requests.post(
            endpoint,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()

        # Ollama returns the generated text under "response"
        return data.get("response", "").strip()
