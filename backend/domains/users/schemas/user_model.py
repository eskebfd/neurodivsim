from typing import List

from pydantic import BaseModel, Field

from backend.domains.models.schemas.attribute import AttributeValueSchema


def _attribute_default(
    value: int,
    minimum: str,
    maximum: str,
) -> AttributeValueSchema:
    return AttributeValueSchema(
        value=value,
        scale_min_description=minimum,
        scale_max_description=maximum,
        explanation="Compatible default value for older user model payloads.",
        confidence="medium",
    )


class UserModelSchema(BaseModel):
    user_type: str = Field(
        ...,
        description="Reference configuration as a simulation-related model assumption.",
    )

    reading_difficulty: AttributeValueSchema = Field(
        ...,
        description="Difficulty reading and processing textual information.",
    )

    sublexical_decoding_stability: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            75,
            "Grapheme-phoneme mapping is very unstable",
            "Grapheme-phoneme mapping remains very stable",
        ),
        description="Stability when decoding unfamiliar words through grapheme-phoneme mappings.",
    )

    orthographic_processing_stability: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            75,
            "Orthographic word processing is very unstable",
            "Orthographic word processing remains very stable",
        ),
        description="Stability when processing familiar and orthographically demanding word forms.",
    )

    parallel_letter_processing_stability: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            75,
            "Several letters are hardly processed in parallel",
            "Several letters are processed very stably in parallel",
        ),
        description="Stability when processing several letters in parallel rather than reading letter by letter.",
    )

    attention_stability: AttributeValueSchema = Field(
        ...,
        description="Stability of attention across several steps; higher values indicate more stable attention.",
    )

    distraction_sensitivity: AttributeValueSchema = Field(
        ...,
        description="Sensitivity to distractions.",
    )

    task_switching_difficulty: AttributeValueSchema = Field(
        ...,
        description="Difficulty switching between tasks, contexts or partial actions.",
    )

    vigilance_stability: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            78,
            "Sustained attention declines very quickly",
            "Sustained attention remains very stable",
        ),
        description="Stability of sustained attention across longer processing phases.",
    )

    inhibitory_control: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            78,
            "Inappropriate responses are hardly inhibited",
            "Inappropriate responses are inhibited very stably",
        ),
        description="Ability to inhibit irrelevant stimuli or premature actions.",
    )

    attention_switching_stability: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            78,
            "Attention switching is very unstable",
            "Attention switching remains very stable",
        ),
        description="Stability when switching between stimuli, steps or contexts in a controlled way.",
    )

    divided_attention_capacity: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            78,
            "Several information sources can hardly be considered in parallel",
            "Several information sources can be considered very well in parallel",
        ),
        description="Ability to attend to several relevant information sources at the same time.",
    )

    omission_tendency: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            20,
            "Very low tendency to miss relevant cues",
            "Very high tendency to miss relevant cues or steps",
        ),
        description="Modeled tendency to omit relevant cues, signals or intermediate steps.",
    )

    reaction_variability: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            20,
            "Responses are very consistent",
            "Responses vary strongly",
        ),
        description="Variability of reaction speed during processing.",
    )

    working_memory_stability: AttributeValueSchema = Field(
        ...,
        description="Stability of working memory during interaction.",
    )

    assumptions: List[str] = Field(
        default_factory=list,
        description="Kurze Annahmen zur Herleitung der values.",
    )


class ProfiledUserModelSchema(BaseModel):
    profile_id: str = Field(
        ...,
        min_length=1,
        description="Stable ID of the associated reference configuration.",
    )
    label: str = Field(..., min_length=1, description="Readable name of the reference configuration.")
    is_baseline: bool = Field(
        False,
        description="Marks the generic comparison configuration.",
    )
    user_model: UserModelSchema
