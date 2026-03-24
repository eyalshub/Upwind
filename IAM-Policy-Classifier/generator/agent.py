# iam_policy_classifier/generator/agent.py

import json
import re  
from pathlib import Path
from typing import Dict, Any

from iam_policy_classifier.generator.schemas import (
    PolicyGenerationRequest,
    PolicyGenerationResult,
)
from iam_policy_classifier.providers.base import LLMProvider
from iam_policy_classifier.config import config


class IAMPolicyGeneratorAgent:
    """
    Agent responsible for generating IAM policies
    based on a reference example policy.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def generate(
        self,
        request: PolicyGenerationRequest
    ) -> PolicyGenerationResult:
        """
        Generate IAM policies that are structurally similar
        to the provided example policy.
        """
        prompt = self._build_prompt(request)

        print(f"DEBUG: Sending prompt to model {config.default_model}...")
        
        raw_response = self.llm.complete(
            prompt=prompt,
            model=config.default_model,
            temperature=config.default_temperature,
            max_tokens=config.default_max_tokens,
        )
        
        print("DEBUG: Raw response received.")
        # print(raw_response) # Uncomment for deep debugging

        return self._parse_response(raw_response)

    def _build_prompt(self, request: PolicyGenerationRequest) -> str:
        """
        Build the LLM prompt using the example policy and generation parameters.
        """
        # Assumes the file exists at this path
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "generator.yaml"

        
        # If running from a different root, specific adjustment might be needed:
        if not prompt_path.exists():
             # Fallback logic or explicit path fix
             prompt_path = Path("prompts/generator.yaml") 

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        prompt_template = prompt_path.read_text(encoding="utf-8")

        example_policy_json = json.dumps(
            request.example_policy,
            indent=2,
            ensure_ascii=False
        )

        prompt = (
            prompt_template
            .replace("{{example_policy}}", example_policy_json)
            .replace("{{count}}", str(request.count))
        )

        return prompt

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Robustly extract JSON object from text (handles Markdown blocks).
        """
        text = text.strip()
        
        # 1. Try regex to find valid JSON block {}
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            blob = match.group(0)
            try:
                return json.loads(blob)
            except json.JSONDecodeError:
                pass # Try raw text if regex captured something partial

        # 2. Try raw text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"Could not extract JSON from LLM output:\n{text}")

    def _parse_response(self, raw_response: str) -> PolicyGenerationResult:
        """
        Parse and validate the LLM response into a structured result.
        """
        try:
            parsed = self._extract_json(raw_response)
        except ValueError as e:
            raise ValueError(
                f"Failed to parse LLM response as JSON.\n"
                f"Raw response:\n{raw_response}"
            ) from e

        try:
            return PolicyGenerationResult.model_validate(parsed)
        except Exception as e:
            raise ValueError(
                f"LLM response does not match PolicyGenerationResult schema.\n"
                f"Parsed JSON:\n{parsed}"
            ) from e