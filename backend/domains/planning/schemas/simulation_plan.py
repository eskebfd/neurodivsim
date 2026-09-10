from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.domains.evaluation.schemas.evaluation_metrics import (
    EvaluationDimensionDefinition,
    EvaluationGoalDefinition,
    EvaluationMetricDefinition,
)


AttributeCategory = Literal[
    "user",
    "task",
    "interface",
    "environment",
    "computed",
    "state",
    "metric",
]
ComputationModelType = Literal[
    "weighted_sum",
    "difference",
    "ratio",
    "threshold",
    "interaction",
]
RequiredModelType = Literal["user", "task", "interface", "environment"]
ModelInstanceScope = Literal["per_profile", "shared"]
ParameterValue = float | str | bool


class SimulationPlanBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserProfileSelection(SimulationPlanBaseModel):
    profile_id: str = Field(
        ...,
        min_length=1,
        description="Stable ID of the selected reference configuration.",
    )
    label: str = Field(
        ...,
        min_length=1,
        description="Readable name of the reference configuration.",
    )
    is_baseline: bool = Field(
        False,
        description="Marks the profile as the comparison baseline.",
    )


class RequiredModelDefinition(SimulationPlanBaseModel):
    model_type: RequiredModelType = Field(
        ...,
        description="Required conceptual model type.",
    )
    instance_scope: ModelInstanceScope = Field(
        "shared",
        description="Defines whether the model is shared or generated per profile.",
    )
    required: bool = Field(
        True,
        description="Indicates whether the model is required for the simulation.",
    )


class RequiredAttribute(SimulationPlanBaseModel):
    attribute_id: str = Field(
        ...,
        min_length=1,
        description="Stable ID of the required attribute.",
    )
    name: str = Field(..., min_length=1, description="Readable attribute name.")
    category: AttributeCategory = Field(
        ...,
        description="Conceptual source or role of the attribute.",
    )
    required_for_metrics: list[str] = Field(
        default_factory=list,
        description="IDs of the metrics that require this attribute.",
    )
    editable: bool = Field(
        False,
        description="Indicates whether the attribute value can be edited before simulation.",
    )


class ComputationModelInstance(SimulationPlanBaseModel):
    model_id: str = Field(
        ...,
        min_length=1,
        description="Stable ID of the computation model instance.",
    )
    name: str = Field(..., min_length=1, description="Readable model name.")
    model_type: ComputationModelType = Field(
        ...,
        description="Deterministic type of the computation model.",
    )
    inputs: list[str] = Field(
        ...,
        min_length=1,
        description="Attribute or model IDs of the input variables.",
    )
    output: str = Field(
        ...,
        min_length=1,
        description="ID of the generated output variable.",
    )
    weights: dict[str, float] | None = Field(
        None,
        description="Optional deterministic weights of the input variables.",
    )
    parameters: dict[str, ParameterValue] | None = Field(
        None,
        description="Optional parameters of the computation model instance.",
    )
    interpretation: str | None = Field(
        None,
        description="Optional conceptual interpretation of the calculation.",
    )


class SimulationSettings(SimulationPlanBaseModel):
    time_step_seconds: float = Field(
        1.0,
        gt=0,
        le=60,
        description="Temporal resolution of the simulation in seconds.",
    )
    max_duration_seconds: float = Field(
        ...,
        gt=0,
        description="Maximum simulation duration in seconds.",
    )
    event_thresholds: dict[str, float] | None = Field(
        None,
        description="Optional event thresholds of the simulation.",
    )

    @model_validator(mode="after")
    def validate_duration(self):
        if self.max_duration_seconds < self.time_step_seconds:
            raise ValueError(
                "max_duration_seconds must be at least time_step_seconds"
            )
        return self


class SimulationPlanSchema(SimulationPlanBaseModel):
    selected_user_profiles: list[UserProfileSelection] = Field(
        ...,
        min_length=1,
        description="Reference configurations that are simulated separately later.",
    )
    evaluation_metrics: list[EvaluationMetricDefinition] = Field(
        ...,
        min_length=1,
        description="Evaluation metrics of the simulation run.",
    )
    evaluation_goals: list[EvaluationGoalDefinition] = Field(
        default_factory=list,
        description="Methodological evaluation goals from which metrics were derived.",
    )
    evaluation_dimensions: list[EvaluationDimensionDefinition] = Field(
        default_factory=list,
        description="Evaluation dimensions and criteria used to derive the metrics.",
    )
    required_models: list[RequiredModelDefinition] = Field(
        default_factory=list,
        description="Required conceptual models and their instantiation scope.",
    )
    required_attributes: list[RequiredAttribute] = Field(
        default_factory=list,
        description="Attributes required for calculation and evaluation.",
    )
    computed_parameters: dict[str, float] = Field(
        default_factory=dict,
        description="Task parameters that have already been calculated deterministically.",
    )
    computation_models: list[ComputationModelInstance] = Field(
        default_factory=list,
        description="Deterministic computation models of the simulation plan.",
    )
    simulation_settings: SimulationSettings
