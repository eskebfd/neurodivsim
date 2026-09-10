from backend.domains.evaluation.schemas.evaluation_metrics import EvaluationGoalDefinition


_EVALUATION_GOALS = (
    EvaluationGoalDefinition(
        goal_id="efficiency",
        name="Efficiency",
        description=(
            "Assesses the modeled time and effort required to complete a task."
        ),
        dimension_ids=[
            "processing_time",
            "completion_efficiency",
            "time_limit_exceedance",
        ],
    ),
    EvaluationGoalDefinition(
        goal_id="effectiveness_and_error_safety",
        name="Effectiveness and Error Safety",
        description=(
            "Assesses whether a task can be completed successfully and with "
            "limited modeled error risk."
        ),
        dimension_ids=[
            "task_success_score",
            "error_risk",
        ],
    ),
    EvaluationGoalDefinition(
        goal_id="cognitive_demand",
        name="Cognitive Demand",
        description=(
            "Assesses how strongly the task draws on modeled cognitive resources."
        ),
        dimension_ids=[
            "cognitive_load",
            "load_related_error_risk",
        ],
    ),
    EvaluationGoalDefinition(
        goal_id="profile_accessibility",
        name="Accessibility across Cognitive Reference Configurations",
        description=(
            "Assesses whether relevant differences occur between the selected "
            "cognitive reference configurations."
        ),
        dimension_ids=[
            "profile_time_differences",
            "profile_success_differences",
            "profile_cognitive_load_differences",
            "profile_error_risk_differences",
        ],
    ),
)

_GOALS_BY_ID = {goal.goal_id: goal for goal in _EVALUATION_GOALS}


def get_evaluation_goals() -> list[EvaluationGoalDefinition]:
    return [goal.model_copy(deep=True) for goal in _EVALUATION_GOALS]


def get_evaluation_goal_by_id(goal_id: str) -> EvaluationGoalDefinition | None:
    goal = _GOALS_BY_ID.get(goal_id)
    return goal.model_copy(deep=True) if goal is not None else None
