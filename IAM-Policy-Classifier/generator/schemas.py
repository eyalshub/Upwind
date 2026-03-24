#iam_policy_classifier/generator/schemas.py
from typing import List, Dict
from pydantic import BaseModel, Field


class PolicyGenerationRequest(BaseModel):
    """
    Request schema for the IAM Policy Generator Agent.
    The generator produces policies similar to a given example policy.
    """
    example_policy: Dict = Field(
        ...,
        description="Reference IAM policy used as a template for generation"
    )
    count: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Number of similar policies to generate"
    )


class GeneratedPolicy(BaseModel):
    """
    A single generated IAM policy.
    """
    policy: Dict


class PolicyGenerationResult(BaseModel):
    """
    Output schema returned by the Generator Agent.
    """
    generated_policies: List[GeneratedPolicy]
