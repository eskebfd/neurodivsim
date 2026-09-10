from typing import List

from pydantic import BaseModel, Field

from backend.domains.models.schemas.attribute import AttributeValueSchema


class EnvironmentModelSchema(BaseModel):
    noise_level: AttributeValueSchema = Field(
        ...,
        description="Noise level of the usage context.",
    )

    distractions: AttributeValueSchema = Field(
        ...,
        description="Allgemeine Ablenkungsbelastung durch die Environment.",
    )

    time_pressure: AttributeValueSchema = Field(
        ...,
        description="Zeitdruck der Usage context.",
    )

    context_stability: AttributeValueSchema = Field(
        ...,
        description="Stability and predictability of the usage context.",
    )

    visual_distraction: AttributeValueSchema
    interruption_risk: AttributeValueSchema
    social_pressure: AttributeValueSchema
    device_constraints: AttributeValueSchema
    lighting_quality: AttributeValueSchema
    mobility_context: AttributeValueSchema

    external_interruption_frequency: AttributeValueSchema = Field(
        default_factory=lambda: AttributeValueSchema(
            value=25,
            scale_min_description="Kaum externe Unterbrechungen",
            scale_max_description="Very frequent external interruptions",
            explanation="Compatible default value for older environment model payloads.",
            confidence="medium",
        ),
        description="Frequency of external interruptions during the task.",
    )

    attention_recovery_support: AttributeValueSchema = Field(
        default_factory=lambda: AttributeValueSchema(
            value=65,
            scale_min_description="Recovery after distraction is hardly supported",
            scale_max_description="Recovery after distraction is strongly supported",
            explanation="Compatible default value for older environment model payloads.",
            confidence="medium",
        ),
        description="Extent to which the environment supports recovery after distraction.",
    )

    assumptions: List[str] = Field(
        default_factory=list,
        description="Kurze Annahmen zur Herleitung der environment values.",
    )
