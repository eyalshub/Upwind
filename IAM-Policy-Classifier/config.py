# iam_policy_classifier/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class AppConfig:
    # Provider selection
    default_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    # Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Model defaults
    default_model: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
    default_temperature: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.0"))
    default_max_tokens: int = int(os.getenv("DEFAULT_MAX_TOKENS", "600"))


config = AppConfig()
