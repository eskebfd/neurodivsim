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
        explanation="Compatible default value for older task model payloads.",
        confidence="medium",
    )


class GOMSOperationEstimateSchema(BaseModel):
    operation: str
    estimated_duration_seconds: float = Field(..., ge=0)
    cognitive_requirement: str = ""


class TaskStepSchema(BaseModel):
    step_id: str = Field(
        ...,
        description="Stable ID of the HTA step, e.g., step_1.",
    )

    name: str = Field(
        ...,
        description="Kurzer Name des Bearbeitungsschritts.",
    )

    goal: str = Field(
        ...,
        description="Goal of the step within the task.",
    )

    step_type: str = Field(
        ...,
        description="Type of step, e.g., read, select, input, decide, check or submit.",
    )

    description: str = Field(
        ...,
        description="Kurze description of the Handlung.",
    )

    goms_operations: List[str] = Field(
        default_factory=list,
        description="GOMS-orientierte Teiloperationen, z. B. perceive, think, point, click, type.",
    )

    operation_time_estimates: List[GOMSOperationEstimateSchema] = Field(
        default_factory=list,
        description="Time estimate and cognitive requirement per GOMS operation.",
    )

    cognitive_requirements: List[str] = Field(
        default_factory=list,
        description="Cognitive requirements of this HTA step.",
    )

    estimated_duration_seconds: float = Field(
        ...,
        ge=1,
        description="Estimated completion time of this step in seconds.",
    )


class TaskModelSchema(BaseModel):
    task_name: str = Field(
        ...,
        description="Name der Task.",
    )

    task_goal: str = Field(
        ...,
        description="Overall goal of the task.",
    )

    task_complexity: AttributeValueSchema = Field(
        ...,
        description="Overall complexity of the task.",
    )

    number_of_steps: AttributeValueSchema = Field(
        ...,
        description=(
            "Actual number of HTA main steps as long as the value remains "
            "within the existing 0-100 attribute bounds."
        ),
    )

    reading_demand: AttributeValueSchema = Field(
        ...,
        description="Text and reading demand of the task.",
    )

    unfamiliar_word_density: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            20,
            "Hardly any unfamiliar or rare words",
            "Many unfamiliar, rare or domain-specific words",
        ),
        description="Share of unfamiliar, rare or domain-specific words in the task material.",
    )

    orthographic_irregularity: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            20,
            "Mostly simple and regular words",
            "Many orthographically demanding, irregular or foreign-language words",
        ),
        description="Orthographic demand caused by irregular, foreign-language or difficult-to-infer words.",
    )

    morphological_complexity: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            25,
            "Hardly any compound or derived words",
            "Many compound, derived or long word forms",
        ),
        description="Complexity caused by long, compound or morphologically derived words.",
    )

    sustained_attention_demand: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            35,
            "Hardly any sustained attention required",
            "Very long uninterrupted attention required",
        ),
        description="Requirement to maintain attention over a longer period.",
    )

    task_switching_demand: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            30,
            "Hardly any switching between steps or contexts",
            "Very frequent switching between steps, stimuli or contexts",
        ),
        description="Demand caused by switching between interaction steps, information or contexts.",
    )

    inhibition_demand: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            25,
            "Hardly any irrelevant stimuli or premature actions to inhibit",
            "Many irrelevant stimuli or premature actions to inhibit",
        ),
        description="Requirement to suppress irrelevant stimuli or unsuitable actions.",
    )

    divided_attention_demand: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            30,
            "Hardly any parallel information sources to consider",
            "Many parallel information sources to consider simultaneously",
        ),
        description="Demand caused by attending to several relevant information sources simultaneously.",
    )

    input_demand: AttributeValueSchema = Field(
        ...,
        description="Demand caused by inputs, selections or form interaction.",
    )

    memory_demand: AttributeValueSchema = Field(
        ...,
        description="Requirement for working memory, ordering or remembering previous information.",
    )

    decision_demand: AttributeValueSchema = Field(
        ...,
        description="Demand caused by decisions and selection alternatives.",
    )

    error_criticality: AttributeValueSchema = Field(
        ...,
        description="Relevance of possible errors for task completion.",
    )

    steps: List[TaskStepSchema] = Field(
        default_factory=list,
        description="HTA-based ordered step sequence with GOMS-oriented time estimation.",
    )

    assumptions: List[str] = Field(
        default_factory=list,
        description="Brief assumptions used to derive the values and steps.",
    )
