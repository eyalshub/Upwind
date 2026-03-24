# iam_policy_classifier/providers/openai_provider.py
from __future__ import annotations

from typing import Optional

from openai import OpenAI

from iam_policy_classifier.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI implementation of the LLMProvider interface.

    This provider is intentionally minimal and supports single-shot
    prompt completion for deterministic classification tasks.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.

        Args:
            api_key: Optional OpenAI API key. If not provided,
                     the SDK will use the OPENAI_API_KEY environment variable.
        """
        self.client = OpenAI(api_key=api_key)

    def complete(
        self,
        *,
        prompt: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        """
        Execute a single-shot completion using OpenAI Chat Completions.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content.strip()
