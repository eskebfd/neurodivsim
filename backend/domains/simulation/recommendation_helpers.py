from collections import defaultdict

from backend.domains.simulation.schemas.recommendations import (
    RecommendationInterpretationContextView,
    RecommendationView,
    StructuredRecommendationView,
)


RECOMMENDATION_THRESHOLDS = {
    "minimum_absolute_delay_seconds": 5,
    "minimum_relative_delay": 0.25,
    "critical_attention": 45,
    "notable_attention": 60,
    "critical_reading_speed": 65,
    "notable_reading_speed": 75,
    "notable_cognitive_load": 65,
    "critical_cognitive_load": 75,
    "notable_error_risk": 55,
    "critical_error_risk": 70,
    "notable_fatigue": 60,
}

READING_OPERATIONS = {"read", "perceive"}
NAVIGATION_OPERATIONS = {"point", "click", "move", "perceive"}
INPUT_OPERATIONS = {"type", "keystroke", "input"}
DECISION_OPERATIONS = {"think", "decide", "choose", "compare"}

EVENT_LABELS = {
    "very_low_attention": "very low attention",
    "very_high_cognitive_load": "high cognitive load",
    "high_error_risk": "elevated error risk",
    "rework_event": "rework/correction",
    "time_pressure_warning": "time pressure",
    "task_aborted": "abort",
}

EVENT_TO_METRIC_IDS = {
    "very_low_attention": ["error_risk", "completion_time", "task_success_score"],
    "very_high_cognitive_load": ["cognitive_load", "error_risk", "task_success_score"],
    "high_error_risk": ["error_risk", "task_success_score"],
    "rework_event": ["completion_time", "completion_efficiency", "task_success_score"],
    "time_pressure_warning": ["time_limit_risk", "completion_time", "error_risk"],
    "task_aborted": ["task_success_score", "completion_efficiency", "completion_time"],
    "high_inhibition_load": ["cognitive_load", "error_risk"],
    "task_switching_strain": ["cognitive_load", "completion_time", "error_risk"],
}


def _number(value, default: float = 0.0) -> float:
    return float(value) if isinstance(value, int | float) else default


def _metric(metrics: dict, metric_id: str) -> float:
    if metric_id == "task_success_score":
        return _number(
            metrics.get("task_success_score", metrics.get("task_success_probability"))
        )
    return _number(metrics.get(metric_id))


def _step_label(step: dict) -> str:
    return step.get("display_name") or step.get("description") or step.get("name") or "interaction step"


def _step_operations(step: dict) -> set[str]:
    operations = step.get("goms_operations") or step.get("operations") or []
    if isinstance(operations, str):
        operations = [operations]
    return {str(operation).lower() for operation in operations}


def _step_type(step: dict) -> str:
    return str(step.get("step_type") or "").lower()


def _is_reading_step(step: dict) -> bool:
    lowered = " ".join(
        str(step.get(key, "")).lower()
        for key in ("name", "description", "display_name")
    )
    return (
        _step_type(step) in {"read", "inspect", "review"}
        or bool(_step_operations(step) & READING_OPERATIONS)
        or any(word in lowered for word in ("read", "review", "inspect", "information", "text"))
    )


def _is_input_step(step: dict) -> bool:
    lowered = " ".join(
        str(step.get(key, "")).lower()
        for key in ("name", "description", "display_name")
    )
    return (
        _step_type(step) in {"input", "type", "form"}
        or bool(_step_operations(step) & INPUT_OPERATIONS)
        or any(word in lowered for word in ("enter", "form", "field", "submit", "confirm", "booking"))
    )


def _is_decision_step(step: dict) -> bool:
    lowered = " ".join(
        str(step.get(key, "")).lower()
        for key in ("name", "description", "display_name")
    )
    return (
        _step_type(step) in {"decision", "choose", "compare"}
        or bool(_step_operations(step) & DECISION_OPERATIONS)
        or any(word in lowered for word in ("select", "compare", "decide", "option", "offer"))
    )


def _is_navigation_step(step: dict) -> bool:
    lowered = " ".join(
        str(step.get(key, "")).lower()
        for key in ("name", "description", "display_name")
    )
    return (
        _step_type(step) in {"navigate", "click", "select"}
        or bool(_step_operations(step) & NAVIGATION_OPERATIONS)
        or any(word in lowered for word in ("click", "button", "navigation", "card", "open", "select"))
    )


def _rows_by_step(timeline: list[dict]) -> dict[str, list[dict]]:
    rows: dict[str, list[dict]] = defaultdict(list)
    for item in timeline:
        step = item.get("current_task_step") or {}
        step_id = step.get("step_id") or str(step.get("step_index", 0))
        rows[str(step_id)].append(item)
    return rows


def _events_for_rows(rows: list[dict]) -> list[dict]:
    return [event for row in rows for event in row.get("events", [])]


def _event_types(events: list[dict]) -> set[str]:
    return {str(event.get("event_type")) for event in events}


def _event_labels(events: list[dict]) -> list[str]:
    labels = []
    for event in events:
        label = EVENT_LABELS.get(event.get("event_type"), event.get("event_type", "Event"))
        if label not in labels:
            labels.append(label)
    return labels


def _event_ids(events: list[dict]) -> list[str]:
    ids = []
    for event in events:
        event_type = str(event.get("event_type", ""))
        if event_type and event_type not in ids:
            ids.append(event_type)
    return ids


def _metric_ids_for_events(events: list[dict], fallback: list[str]) -> list[str]:
    metric_ids = []
    for event_id in _event_ids(events):
        for metric_id in EVENT_TO_METRIC_IDS.get(event_id, []):
            if metric_id not in metric_ids:
                metric_ids.append(metric_id)
    for metric_id in fallback:
        if metric_id not in metric_ids:
            metric_ids.append(metric_id)
    return metric_ids


def _ui_component_for_step(step: dict) -> str:
    if _is_input_step(step):
        return "input or confirmation element"
    if _is_decision_step(step):
        return "selection or comparison area"
    if _is_navigation_step(step):
        return "navigation or next action"
    if _is_reading_step(step):
        return "text or information area"
    return "affected interface area"


def _structured_recommendation(
    *,
    step: dict,
    events: list[dict],
    fallback_metric_ids: list[str],
    cause: str,
    severity: str,
    design_principle: str,
    general_recommendation: str,
    priority: str,
    rule_id: str,
) -> StructuredRecommendationView:
    return StructuredRecommendationView(
        triggering_metric_ids=_metric_ids_for_events(events, fallback_metric_ids),
        triggering_event_ids=_event_ids(events),
        affected_task_step_id=str(step.get("step_id") or "") or None,
        affected_task_step_name=_step_label(step),
        affected_ui_component=_ui_component_for_step(step),
        cause=cause,
        severity=severity,
        design_principle=design_principle,
        general_recommendation=general_recommendation,
        priority=priority,
        rule_id=rule_id,
    )


def _with_interpretation_context(
    recommendation: RecommendationView,
) -> RecommendationView:
    recommendation.interpretation_context = RecommendationInterpretationContextView(
        must_not_change=[
            "triggering_metric_ids",
            "triggering_event_ids",
            "affected_task_step_id",
            "severity",
            "priority",
            "rule_id",
        ],
        structured_recommendation=recommendation.structured_recommendation,
    )
    return recommendation


def _step_stats(rows: list[dict]) -> dict[str, float]:
    if not rows:
        return {
            "min_attention": 100,
            "max_fatigue": 0,
            "max_cognitive_load": 0,
            "max_error_risk": 0,
            "min_reading_speed": 100,
        }
    return {
        "min_attention": min(_number(row.get("attention"), 100) for row in rows),
        "max_fatigue": max(_number(row.get("fatigue")) for row in rows),
        "max_cognitive_load": max(_number(row.get("cognitive_load")) for row in rows),
        "max_error_risk": max(_number(row.get("error_risk")) for row in rows),
        "min_reading_speed": min(_number(row.get("reading_speed"), 100) for row in rows),
    }


def _delay_values(step: dict) -> tuple[float, float, float]:
    planned = _number(step.get("planned_duration_seconds")) or _number(step.get("base_step_duration"))
    actual = _number(step.get("actual_duration_seconds")) or _number(step.get("actual_step_duration"))
    delay = max(0.0, actual - planned)
    relative = delay / planned if planned else 0.0
    return planned, actual, relative


def _is_significant_delay(step: dict) -> bool:
    planned, actual, relative = _delay_values(step)
    return (
        actual - planned >= RECOMMENDATION_THRESHOLDS["minimum_absolute_delay_seconds"]
        and relative >= RECOMMENDATION_THRESHOLDS["minimum_relative_delay"]
    )


HIGH_PRIORITY_EVENT_TYPES = {"task_aborted", "rework_event"}
STRONG_SIGNAL_EVENT_TYPES = {
    "high_error_risk",
    "very_high_cognitive_load",
    "very_low_attention",
    "high_inhibition_load",
    "task_switching_strain",
    "time_pressure_warning",
}


def _priority(
    *,
    critical: bool = False,
    event_count: int = 0,
    relative_delay: float = 0.0,
    event_types: set[str] | None = None,
) -> str:
    event_types = event_types or set()
    strong_event_count = len(event_types & STRONG_SIGNAL_EVENT_TYPES)
    if critical or event_types & HIGH_PRIORITY_EVENT_TYPES:
        return "high"
    if relative_delay >= 0.65:
        return "high"
    if strong_event_count >= 3:
        return "high"
    if strong_event_count >= 2 and relative_delay >= 0.35:
        return "high"
    if event_count >= 1 or relative_delay >= 0.25:
        return "medium"
    return "low"


def _confidence(evidence_count: int, has_event: bool) -> str:
    if has_event and evidence_count >= 3:
        return "high"
    if evidence_count >= 2:
        return "medium"
    return "low"


def _contextual_error_reasoning(
    *,
    profile_label: str,
    step: dict,
    stats: dict[str, float],
    events: list[dict],
) -> str:
    step_name = _step_label(step)
    event_hint = ""
    if events:
        event_hint = (
            " In addition, the following events were detected in this step: "
            f"{', '.join(_event_labels(events))}."
        )
    if _is_input_step(step):
        return (
            f'The step "{step_name}" likely contains an input, confirmation, '
            "or another error-sensitive action. The elevated "
            f"error risk of {stats['max_error_risk']:.1f} out of 100 indicates "
            f"that {profile_label} requires more guidance and clearer feedback "
            "before the action is completed."
            f"{event_hint}"
        )
    if _is_decision_step(step):
        return (
            f'The step "{step_name}" likely requires comparison, selection, '
            "or weighing several options. The elevated error risk indicates "
            "that differences, selection criteria or consequences of the decision "
            f"are not sufficiently visible for {profile_label}."
            f"{event_hint}"
        )
    if _is_reading_step(step):
        return (
            f'The step "{step_name}" primarily involves processing information. '
            "If error risk occurs here, the barrier is more likely to concern "
            "unclear text structure, difficult-to-compare information or missing "
            f"orientation than form fields. {profile_label} requires information "
            "guidance that is easier to parse at this point."
            f"{event_hint}"
        )
    return (
        f'In step "{step_name}", the next action must be clearly recognizable. '
        f"The elevated error risk of {stats['max_error_risk']:.1f} out of 100 "
        "indicates that labels, status information or feedback do not guide the "
        f"person sufficiently through this step.{event_hint}"
    )


def _contextual_fallback_actions(step: dict) -> list[str]:
    if _is_reading_step(step):
        primary_action = (
            "introduce the section with a clear subheading and a brief "
            "key message"
        )
    elif _is_decision_step(step):
        primary_action = (
            "make the most important decision criteria visible directly next to the options"
        )
    elif _is_input_step(step):
        primary_action = (
            "explain required fields, current selection and next step directly at the input area"
        )
    elif _is_navigation_step(step):
        primary_action = (
            "clarify the next expected click through labeling, position or emphasis"
        )
    else:
        primary_action = (
            "make the most important information and the next action more visible within the step"
        )
    return [
        primary_action,
        "reduce unnecessary additional information in this step",
        "optionally observe in a short usability test whether this point still creates uncertainty",
    ]
