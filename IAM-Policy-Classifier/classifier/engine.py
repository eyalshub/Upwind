#iam_policy_classifier/classifier/engine.py
from __future__ import annotations

import json
import re
from typing import Optional, Any, Dict

import yaml
from pydantic import ValidationError

from iam_policy_classifier.classifier.schemas import (
    IAMPolicy,
    ClassificationResult,
    EngineConfig,
)
from iam_policy_classifier.classifier.prompt_loader import build_classification_prompt
from iam_policy_classifier.providers.base import LLMProvider


# ------------------------------------------------------------------
# Robust JSON / YAML extraction
# ------------------------------------------------------------------
import json
import re
from typing import Dict, Any

def _extract_json(text: str) -> Dict[str, Any]:
    """
    Robustly extract structured data from LLM output.
    Handles Markdown fences, extra fields, and partial failures.
    """
    cleaned = text.strip()
    if "```" in cleaned:
        pattern = r"```(?:json)?\s*(.*?)\s*```"
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)


    start_idx = cleaned.find('{')
    end_idx = cleaned.rfind('}')

    if start_idx != -1 and end_idx != -1:
        json_candidate = cleaned[start_idx : end_idx + 1]
        try:
            data = json.loads(json_candidate)
            
            data_lower = {k.lower(): v for k, v in data.items()}
            
            if "classification" in data_lower:
                return {
                    "classification": data_lower["classification"],
                    "reason": data_lower.get("reason", "No reason provided"),
                    "policy": data_lower.get("policy") 
                }
        except json.JSONDecodeError:
            pass 


    
    classification_match = re.search(
        r'"classification"\s*:\s*"([^"]+)"', 
        cleaned, 
        re.IGNORECASE
    )
    
    reason_match = re.search(
        r'"reason"\s*:\s*"([^"]+)"', 
        cleaned, 
        re.IGNORECASE
    )

    if not classification_match:
        raise ValueError(f"Unrecoverable LLM output:\n{text}")

    return {
        "classification": classification_match.group(1),
        "reason": reason_match.group(1) if reason_match else "No reason extracted",
        "policy": None 
    }


# ------------------------------------------------------------------
# Final stabilization layer
# ------------------------------------------------------------------
def _finalize_output(
    parsed: Dict[str, Any],
    original_policy: IAMPolicy,
) -> Dict[str, Any]:
    parsed["policy"] = original_policy.model_dump()

    classification = parsed.get("classification")

    if isinstance(classification, dict):
        if "enum" in classification and classification["enum"]:
            classification = classification["enum"][0]
        elif "value" in classification:
            classification = classification["value"]
        elif "description" in classification:
            classification = classification["description"]

    if not isinstance(classification, str):
        raise ValueError("LLM did not return a valid classification")

    classification = classification.split("|")[0].strip().capitalize()

    if classification not in ("Weak", "Strong"):
        raise ValueError(f"Invalid classification value: {classification}")

    parsed["classification"] = classification

    reason = parsed.get("reason")

    if isinstance(reason, dict) and "description" in reason:
        reason = reason["description"]

    if not isinstance(reason, str) or not reason.strip():
        if classification == "Weak":
            reason = (
                "The policy grants overly broad permissions or lacks sufficient "
                "restrictions, resulting in elevated security risk."
            )
        else:
            reason = (
                "The policy applies scoped permissions and appropriate contextual "
                "restrictions, aligning with security best practices."
            )

    parsed["reason"] = reason.strip()

    return parsed


# ------------------------------------------------------------------
# Core engine
# ------------------------------------------------------------------
class ClassificationEngine:
    """
    Core orchestration layer for IAM policy classification.
    """

    def __init__(
        self,
        provider: LLMProvider,
        config: Optional[EngineConfig] = None,
    ):
        self.provider = provider
        self.config = config or EngineConfig()

    def classify(self, policy: IAMPolicy) -> ClassificationResult:
        """
        Classify an IAM policy as Weak or Strong using an LLM.
        Always returns a ClassificationResult; failures are captured as ERROR.
        """
        try:
            # 1. Build prompt
            prompt = build_classification_prompt(policy)

            # 2. Call LLM
            raw_response = self.provider.complete(
                prompt=prompt,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            if not raw_response or not raw_response.strip():
                raise RuntimeError(
                    f"LLM returned empty response "
                    f"(provider={self.provider.name}, model={self.config.model})"
                )

            # 3. Extract structured output
            parsed = _extract_json(raw_response)

            # 4. Final stabilization
            parsed = _finalize_output(parsed, policy)

            # 5. Validate schema
            return ClassificationResult.model_validate(parsed)

        except Exception as exc:
            # 🔒 FAIL SAFE: never crash the experiment
            return ClassificationResult(
                policy=policy.model_dump(),
                classification="ERROR",
                reason=str(exc),
            )

