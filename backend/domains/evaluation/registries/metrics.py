from backend.domains.evaluation.schemas.evaluation_metrics import (
    EvaluationMetricDefinition,
    EvaluationMetricsSelection,
)


_PREDEFINED_EVALUATION_METRICS = (
    EvaluationMetricDefinition(
        metric_id="cognitive_load",
        name="Cognitive Load",
        description=(
            "Modeled mental demand during task processing on the internal "
            "0-100 scale."
        ),
        metric_type="score",
        source="predefined",
        analysis_question="How does cognitive load develop across the interaction?",
        data_basis="Task, text, navigation and fatigue values",
        limitation="Heuristic load score, not a clinical measure.",
        expected_output_range=(0, 100),
        higher_is_better=False,
        tags=["cognition", "workload"],
    ),
    EvaluationMetricDefinition(
        metric_id="error_risk",
        name="Error Risk",
        description=(
            "Heuristic risk score for error-prone interactions on the internal "
            "0-100 scale; not empirically calibrated."
        ),
        metric_type="score",
        source="predefined",
        analysis_question="At which steps is the modeled error risk elevated?",
        data_basis="Cognitive Load, Fatigue, Time Pressure and Attention",
        limitation="Risk score, not an empirically calibrated probability.",
        expected_output_range=(0, 100),
        higher_is_better=False,
        tags=["error", "risk"],
    ),
    EvaluationMetricDefinition(
        metric_id="completion_efficiency",
        name="Completion Efficiency",
        description=(
            "Heuristic efficiency score for modeled task completion on the "
            "internal 0-100 scale."
        ),
        metric_type="score",
        source="predefined",
        analysis_question="How fluently can the modeled task be completed?",
        data_basis="Reading Speed, Attention and Task Success Score",
        limitation="Comparative simulation score, not measured usage time.",
        expected_output_range=(0, 100),
        higher_is_better=True,
        tags=["completion", "efficiency"],
    ),
    EvaluationMetricDefinition(
        metric_id="task_success_score",
        name="Task Success Score",
        description=(
            "Heuristic task success score on the internal 0-100 scale; not a "
            "statistically calibrated probability."
        ),
        metric_type="score",
        source="predefined",
        analysis_question="How favorable are the modeled conditions for task completion?",
        data_basis="Error Risk, Cognitive Load and Navigation Effort",
        limitation="Heuristic score, not a statistical success probability.",
        expected_output_range=(0, 100),
        higher_is_better=True,
        tags=["success", "score"],
    ),
    EvaluationMetricDefinition(
        metric_id="completion_time",
        name="Completion Time",
        description="Total simulated duration until task completion in seconds.",
        metric_type="time",
        source="predefined",
        analysis_question="How long does the full modeled task take?",
        data_basis="Task Progress, GOMS base durations and profile states",
        limitation="Simulated completion time, not measured usage time.",
        expected_output_range=(0, 3600),
        higher_is_better=False,
        tags=["time", "completion"],
    ),
    EvaluationMetricDefinition(
        metric_id="time_limit_risk",
        name="Time Limit Risk",
        description=(
            "Heuristic risk score for exceeding a specified time limit; not an "
            "empirically calibrated probability."
        ),
        metric_type="score",
        source="predefined",
        analysis_question="How critical is the relation between completion time and time limit?",
        data_basis="Completion Time and configured time limit",
        limitation="Heuristic risk score depending on the selected time limit.",
        expected_output_range=(0, 100),
        higher_is_better=False,
        tags=["time", "risk"],
    ),
)

_METRICS_BY_ID = {
    metric.metric_id: metric for metric in _PREDEFINED_EVALUATION_METRICS
}

_RETIRED_METRIC_IDS = {
    "dyslexia_reading_load",
    "adhd_interaction_load",
}

_METRIC_ALIASES = {
    "task_success_probability": "task_success_score",
}


def canonical_metric_id(metric_id: str) -> str:
    return _METRIC_ALIASES.get(metric_id, metric_id)


def get_predefined_evaluation_metrics() -> list[EvaluationMetricDefinition]:
    return [metric.model_copy(deep=True) for metric in _PREDEFINED_EVALUATION_METRICS]


def get_retired_evaluation_metric_ids() -> set[str]:
    return set(_RETIRED_METRIC_IDS)


def get_metric_by_id(metric_id: str) -> EvaluationMetricDefinition | None:
    metric = _METRICS_BY_ID.get(canonical_metric_id(metric_id))
    return metric.model_copy(deep=True) if metric is not None else None


def build_default_evaluation_metrics_selection(
    metric_ids: list[str] | None = None,
) -> EvaluationMetricsSelection:
    selected_ids = metric_ids or [
        metric.metric_id for metric in _PREDEFINED_EVALUATION_METRICS
    ]
    selected_ids = list(
        dict.fromkeys(canonical_metric_id(metric_id) for metric_id in selected_ids)
    )
    selected_ids = [
        metric_id
        for metric_id in selected_ids
        if metric_id not in _RETIRED_METRIC_IDS
    ]
    unknown_ids = [
        metric_id
        for metric_id in selected_ids
        if metric_id not in _METRICS_BY_ID
    ]
    if unknown_ids:
        raise ValueError(
            "Unknown predefined evaluation metric IDs: "
            + ", ".join(unknown_ids)
        )

    return EvaluationMetricsSelection(
        selected_metrics=[
            _METRICS_BY_ID[metric_id].model_copy(deep=True)
            for metric_id in selected_ids
        ]
    )
