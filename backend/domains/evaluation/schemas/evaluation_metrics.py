from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


EvaluationMetricSource = Literal["predefined", "custom", "suggested"]
EvaluationMetricType = Literal[
    "time",
    "count",
    "score",
    "probability",
    "ratio",
    "event",
    "state",
]


class EvaluationMetricsBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvaluationMetricDefinition(EvaluationMetricsBaseModel):
    metric_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Stable technical ID of the evaluation metric.",
    )
    name: str = Field(..., min_length=1, description="Readable metric name.")
    description: str = Field(
        ...,
        min_length=1,
        description="Short domain-specific description of the evaluation metric.",
    )
    metric_type: EvaluationMetricType = Field(
        ...,
        description="Data type or observation type of the metric.",
    )
    source: EvaluationMetricSource = Field(
        ...,
        description="Origin of the metric: predefined, user-defined or suggested.",
    )
    analysis_question: str | None = Field(
        None,
        description="Optional question to be answered by the metric.",
    )
    data_basis: str | None = Field(
        None,
        description="Short domain-specific description of the data basis used.",
    )
    limitation: str | None = Field(
        None,
        description="Short methodological limitation of the metric.",
    )
    expected_output_range: tuple[float, float] | None = Field(
        None,
        description="Optional expected value range with minimum and maximum.",
    )
    higher_is_better: bool | None = Field(
        None,
        description="Optional indication of the preferred metric direction.",
    )
    requires_simulation: bool = Field(
        True,
        description="Indicates whether the metric can only be computed from a simulation.",
    )
    related_user_profiles: list[str] = Field(
        default_factory=list,
        description="Optional profile IDs for which the metric is particularly relevant.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Short keywords for grouping and filtering.",
    )

    @model_validator(mode="after")
    def validate_expected_output_range(self):
        if self.expected_output_range is not None:
            minimum, maximum = self.expected_output_range
            if minimum > maximum:
                raise ValueError(
                    "expected_output_range minimum must not exceed maximum"
                )
        return self


class EvaluationMetricsSelection(EvaluationMetricsBaseModel):
    selected_metrics: list[EvaluationMetricDefinition] = Field(
        ...,
        min_length=1,
        description="Evaluation metrics selected for the simulation plan.",
    )
    custom_metric_requests: list[str] = Field(
        default_factory=list,
        description="Unstructured requests for custom metrics.",
    )
    notes: str | None = Field(
        None,
        description="Optional notes on selection or later evaluation.",
    )


class EvaluationGoalDefinition(EvaluationMetricsBaseModel):
    goal_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Stable technical ID of the evaluation goal.",
    )
    name: str = Field(..., min_length=1, description="Readable goal name.")
    description: str = Field(
        ...,
        min_length=1,
        description="Domain-specific description of the evaluation goal.",
    )
    dimension_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Evaluation dimensions that specify this goal.",
    )


class EvaluationDimensionDefinition(EvaluationMetricsBaseModel):
    dimension_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Stable technical ID of the evaluation dimension.",
    )
    name: str = Field(..., min_length=1, description="Readable dimension name.")
    description: str = Field(
        ...,
        min_length=1,
        description="Domain-specific description of the evaluation dimension.",
    )
    criterion: str = Field(
        ...,
        min_length=1,
        description="Evaluation criterion for favorable or problematic expressions.",
    )
    metric_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Result metrics used to evaluate this dimension.",
    )


class EvaluationGoalSelection(EvaluationMetricsBaseModel):
    selected_goal_ids: list[str] = Field(
        default_factory=list,
        description="Selected evaluation goals.",
    )
    custom_metric_requests: list[str] = Field(
        default_factory=list,
        description="Unstructured requests for additional metrics.",
    )

    @model_validator(mode="after")
    def validate_selection_not_empty(self):
        if not self.selected_goal_ids and not self.custom_metric_requests:
            raise ValueError(
                "At least one evaluation goal or custom metric request is required"
            )
        return self


class ResolvedEvaluationSelection(EvaluationMetricsBaseModel):
    selected_goals: list[EvaluationGoalDefinition] = Field(
        default_factory=list,
        description="Resolved evaluation goals.",
    )
    resolved_dimensions: list[EvaluationDimensionDefinition] = Field(
        default_factory=list,
        description="Evaluation dimensions derived from the selected goals.",
    )
    selected_metrics: EvaluationMetricsSelection = Field(
        ...,
        description="Existing metric selection derived from the dimensions.",
    )
    custom_metric_requests: list[str] = Field(
        default_factory=list,
        description="Included free metric or analysis requests.",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Notes on resolution and methodological limitations.",
    )
