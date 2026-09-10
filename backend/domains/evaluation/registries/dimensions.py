from backend.domains.evaluation.schemas.evaluation_metrics import (
    EvaluationDimensionDefinition,
)


_EVALUATION_DIMENSIONS = (
    EvaluationDimensionDefinition(
        dimension_id="processing_time",
        name="Completion Time",
        description="Considers the time required for full task completion.",
        criterion=(
            "The task should be completed without disproportionate modeled delays."
        ),
        metric_ids=["completion_time"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="completion_efficiency",
        name="Completion Efficiency",
        description="Considers the relation between successful progress and demand.",
        criterion=(
            "A favorable pattern combines high efficiency with a stable Task "
            "Success Score."
        ),
        metric_ids=["completion_efficiency"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="time_limit_exceedance",
        name="Time Limit Risk",
        description="Considers whether completion time may exceed a time limit.",
        criterion=(
            "A high heuristic risk score for exceeding the available time limit "
            "is considered problematic."
        ),
        metric_ids=["time_limit_risk"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="task_success_score",
        name="Task Success Score",
        description="Considers the heuristic score for successful task completion.",
        criterion="A high Task Success Score indicates a favorable modeled pattern.",
        metric_ids=["task_success_score"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="error_risk",
        name="Error Risk",
        description=(
            "Considers the heuristic risk score for error-prone interactions "
            "during the task."
        ),
        criterion="An elevated modeled Error Risk score is considered problematic.",
        metric_ids=["error_risk"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="cognitive_load",
        name="Cognitive Load",
        description="Considers the modeled cognitive demand of a reference configuration.",
        criterion="High modeled Cognitive Load is considered problematic.",
        metric_ids=["cognitive_load"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="load_related_error_risk",
        name="Load-related Error Risk",
        description=(
            "Considers error risks that occur together with cognitive demand "
            "and fatigue."
        ),
        criterion=(
            "Elevated Error Risk together with high Cognitive Load is considered "
            "problematic."
        ),
        metric_ids=["error_risk"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="profile_time_differences",
        name="Differences in Completion Time",
        description=(
            "Considers differences in Completion Time between cognitive "
            "reference configurations."
        ),
        criterion=(
            "Large differences in modeled completion duration between "
            "configurations are considered relevant."
        ),
        metric_ids=["completion_time", "completion_efficiency"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="profile_success_differences",
        name="Differences in Task Success Score",
        description=(
            "Considers differences in Task Success Score between cognitive "
            "reference configurations."
        ),
        criterion=(
            "Markedly lower Task Success Scores for individual configurations "
            "are considered relevant."
        ),
        metric_ids=["task_success_score"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="profile_cognitive_load_differences",
        name="Differences in Cognitive Load",
        description=(
            "Considers differences in Cognitive Load between cognitive "
            "reference configurations."
        ),
        criterion="Markedly higher load values for individual configurations are relevant.",
        metric_ids=["cognitive_load"],
    ),
    EvaluationDimensionDefinition(
        dimension_id="profile_error_risk_differences",
        name="Differences in Error Risk",
        description=(
            "Considers differences in Error Risk between cognitive reference "
            "configurations."
        ),
        criterion="Markedly elevated error risks for individual configurations are relevant.",
        metric_ids=["error_risk"],
    ),
)

_DIMENSIONS_BY_ID = {
    dimension.dimension_id: dimension for dimension in _EVALUATION_DIMENSIONS
}


def get_evaluation_dimensions() -> list[EvaluationDimensionDefinition]:
    return [
        dimension.model_copy(deep=True)
        for dimension in _EVALUATION_DIMENSIONS
    ]


def get_evaluation_dimension_by_id(
    dimension_id: str,
) -> EvaluationDimensionDefinition | None:
    dimension = _DIMENSIONS_BY_ID.get(dimension_id)
    return dimension.model_copy(deep=True) if dimension is not None else None
