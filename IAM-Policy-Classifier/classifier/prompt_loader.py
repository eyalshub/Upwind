# iam_policy_classifier/classifier/prompt_loader.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml

from iam_policy_classifier.classifier.schemas import IAMPolicy


# ------------------------------------------------------------------
# Prompt configuration
# ------------------------------------------------------------------
PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
DEFAULT_PROMPT_FILE = "classifier.yaml"


# ------------------------------------------------------------------
# Loading utilities
# ------------------------------------------------------------------
def load_prompt_yaml(prompt_name: str = DEFAULT_PROMPT_FILE) -> Dict[str, Any]:
    """
    Load a YAML prompt definition from the prompts directory.
    """
    prompt_path = PROMPTS_DIR / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with prompt_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ------------------------------------------------------------------
# Rendering utilities
# ------------------------------------------------------------------
def render_system_instructions(system_block: Dict[str, Any]) -> str:
    """
    Render the system-level instructions section of the prompt.
    """
    lines: list[str] = []

    role = system_block.get("role", {})
    if role:
        lines.append(f"Role: {role.get('title')}")
        lines.append(role.get("description", ""))

    responsibilities = system_block.get("responsibilities", [])
    if responsibilities:
        lines.append("\nResponsibilities:")
        for r in responsibilities:
            lines.append(f"- {r}")

    evaluation = system_block.get("evaluation_criteria", {})
    if evaluation:
        lines.append("\nSecurity Evaluation Criteria:")
        for name, desc in evaluation.items():
            lines.append(f"- {name}: {desc}")

    rules = system_block.get("decision_rules", {})
    if rules:
        lines.append("\nDecision Rules:")
        for name, desc in rules.items():
            lines.append(f"- {name}: {desc}")

    constraints = system_block.get("constraints", [])
    if constraints:
        lines.append("\nConstraints:")
        for c in constraints:
            lines.append(f"- {c}")

    return "\n".join(line for line in lines if line).strip()


def render_user_task(task_block: Dict[str, Any]) -> str:
    """
    Render the user task section of the prompt.
    """
    lines: list[str] = []

    objective = task_block.get("objective")
    if objective:
        lines.append(f"Task Objective:\n{objective}")

    labels = task_block.get("classification_labels")
    if labels:
        lines.append(f"\nAllowed Classification Labels: {', '.join(labels)}")

    return "\n".join(lines).strip()


def render_output_contract(output_block: Dict[str, Any]) -> str:
    """
    Render the output format and schema instructions.
    """
    if "contract" in output_block:
        return f"Output Contract:\n{output_block['contract']}"
    schema = output_block.get("schema", {})
    lines = [
        "Output Format:",
        "Return ONLY valid JSON with the following structure:",
        json.dumps(schema, indent=2),
    ]

    return "\n".join(lines).strip()


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def build_classification_prompt(
    policy: IAMPolicy,
    prompt_name: str = DEFAULT_PROMPT_FILE,
) -> str:
    """
    Build the final prompt string for IAM policy classification.
    """
    prompt_yaml = load_prompt_yaml(prompt_name)

    system_text = render_system_instructions(
        prompt_yaml.get("system_instructions", {})
    )
    user_text = render_user_task(prompt_yaml.get("user_task", {}))
    output_text = render_output_contract(prompt_yaml.get("output", {}))

    policy_json: Any = policy.model_dump(mode="json")

    return f"""
SYSTEM:
{system_text}

USER:
{user_text}

IAM Policy:
{json.dumps(policy_json, indent=2)}

{output_text}
""".strip()
