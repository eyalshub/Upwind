# iam_policy_classifier/classifier/schemas.py
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict, field_validator


# -----------------------------
# IAM Policy (input) schema
# -----------------------------
class PolicyStatement(BaseModel):

    model_config = ConfigDict(extra="allow")

    Effect: Literal["Allow", "Deny"]
    Action: Union[str, List[str]]
    Resource: Union[str, List[str]]
    Condition: Optional[Dict[str, Any]] = None


class IAMPolicy(BaseModel):

    model_config = ConfigDict(extra="allow")

    Version: str
    Statement: Union[PolicyStatement, List[PolicyStatement]]

    @field_validator("Statement")
    @classmethod
    def ensure_statement_list(cls, v):
        if isinstance(v, dict):
            return [v]
        return v


# -----------------------------
# LLM classification output schema
# -----------------------------
ClassificationLabel = Literal["Weak", "Strong","ERROR"]


class ClassificationResult(BaseModel):
    """
    The exact structured output contract required by the task.
    """
    model_config = ConfigDict(extra="forbid")

    policy: Dict[str, Any] = Field(..., description="The original input policy JSON.")
    classification: ClassificationLabel = Field(..., description="Weak or Strong.")
    reason: str = Field(..., min_length=1, description="Short security-focused justification.")


# -----------------------------
# Optional: request/engine configs
# -----------------------------
class EngineConfig(BaseModel):
    """
    Optional config container to keep the engine deterministic & reproducible.
    Not strictly required, but helps keep the project clean.
    """
    model_config = ConfigDict(extra="forbid")

    provider: Literal["openai", "ollama", "huggingface", "bedrock"] = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(600, ge=64, le=4096)


class ClassifyRequest(BaseModel):
    """
    Useful if you later want to expose a CLI/API, but also great for clean code now.
    """
    model_config = ConfigDict(extra="forbid")

    policy: IAMPolicy
    config: Optional[EngineConfig] = None


class ClassifyResponse(BaseModel):
    """
    Wrapper response (optional). If you keep it simple, you can return ClassificationResult directly.
    """
    model_config = ConfigDict(extra="forbid")

    result: ClassificationResult
