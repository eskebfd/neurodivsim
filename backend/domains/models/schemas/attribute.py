from typing import Literal

from pydantic import BaseModel, Field


ConfidenceLevel = Literal["low", "medium", "high"]


class AttributeValueSchema(BaseModel):
    value: int = Field(
        ...,
        ge=0,
        le=100,
        description="Numeric attribute value on a scale from 0 to 100.",
    )

    scale_min_description: str = Field(
        ...,
        description="Description of what a value of 0 means for this attribute.",
    )

    scale_max_description: str = Field(
        ...,
        description="Description of what a value of 100 means for this attribute.",
    )

    explanation: str = Field(
        ...,
        description="Short rationale for assuming this value.",
    )

    confidence: ConfidenceLevel = Field(
        ...,
        description=(
            "LLM confidence in estimating the attribute value. "
            "Independent of value and simulation."
        ),
    )
