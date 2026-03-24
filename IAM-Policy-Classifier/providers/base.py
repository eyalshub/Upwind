# iam_policy_classifier/providers/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    This defines a minimal, stable interface that allows the classification
    engine to remain provider-agnostic.
    """

    @abstractmethod
    def complete(
        self,
        *,
        prompt: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        """
        Execute a single-shot completion call to an LLM.

        Args:
            prompt: Fully rendered prompt string.
            model: Model identifier (provider-specific).
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the response.

        Returns:
            Raw text response from the LLM (expected to be JSON).
        """
        raise NotImplementedError
