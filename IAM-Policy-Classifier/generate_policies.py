# iam_policy_classifier/generate_policies.py

import json
from pathlib import Path

from fastapi import logger

from iam_policy_classifier.generator.agent import IAMPolicyGeneratorAgent
from iam_policy_classifier.generator.schemas import PolicyGenerationRequest
from iam_policy_classifier.providers.openai_provider import OpenAIProvider
from iam_policy_classifier.config import AppConfig, config


def load_policy(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_policy(policy: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(policy, f, indent=2, ensure_ascii=False)


def generate_and_save(
    *,
    example_policy_path: Path,
    output_dir: Path,
    count: int,
):
    # Load example policy
    example_policy = load_policy(example_policy_path)

    # Init LLM + Generator Agent
    llm = OpenAIProvider(
    api_key=config.openai_api_key
)
    generator = IAMPolicyGeneratorAgent(llm_provider=llm)

    # Generate policies
    request = PolicyGenerationRequest(
        example_policy=example_policy,
        count=count,
    )

    result = generator.generate(request)

    # Save generated policies
    for idx, generated in enumerate(result.generated_policies, start=1):
        filename = f"{example_policy_path.stem}_generated_{idx:03}.json"
        output_path = output_dir / filename
        save_policy(generated.policy, output_path)

        print(f"[✓] Saved: {output_path}")


def main():
    base_dir = Path(__file__).resolve().parent

    policies_dir = base_dir / "policies"
    try:
        llm_provider = OpenAIProvider(api_key=config.openai_api_key)
        agent = IAMPolicyGeneratorAgent(llm_provider=llm_provider)
    except Exception as e:
        logger.critical(f"Failed to initialize LLM Provider: {e}")
        return
    # ---- Weak ----
    generate_and_save(
        example_policy_path=policies_dir / "weak_policy.json",
        output_dir=policies_dir / "weak",
        count=5,
    )

    # ---- Strong ----
    generate_and_save(
        example_policy_path=policies_dir / "strong_policy.json",
        output_dir=policies_dir / "strong",
        count=5,
    )


if __name__ == "__main__":
    main()
