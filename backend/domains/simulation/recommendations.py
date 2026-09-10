from backend.domains.simulation.schemas.recommendations import (
    PositiveFindingView,
    RecommendationView,
)

from backend.domains.simulation.recommendation_helpers import (
    RECOMMENDATION_THRESHOLDS,
    _confidence,
    _contextual_error_reasoning,
    _contextual_fallback_actions,
    _delay_values,
    _event_labels,
    _event_types,
    _events_for_rows,
    _is_decision_step,
    _is_input_step,
    _is_reading_step,
    _is_significant_delay,
    _metric,
    _priority,
    _rows_by_step,
    _step_label,
    _step_stats,
    _structured_recommendation,
    _with_interpretation_context,
)


def _make_text_recommendation(
    *,
    profile_id: str,
    profile_label: str,
    step: dict,
    rows: list[dict],
    events: list[dict],
) -> RecommendationView:
    planned, actual, relative = _delay_values(step)
    stats = _step_stats(rows)
    evidence = [
        f"base time {planned:.0f} seconds, simulated time {actual:.0f} seconds",
        f"relative time deviation {relative * 100:.0f} %",
        f"lowest reading speed {stats['min_reading_speed']:.1f} out of 100",
    ]
    if stats["max_cognitive_load"] >= RECOMMENDATION_THRESHOLDS["notable_cognitive_load"]:
        evidence.append(f"cognitive load up to {stats['max_cognitive_load']:.1f} out of 100")
    if events:
        evidence.append("Events: " + ", ".join(_event_labels(events)))
    priority = _priority(
        event_count=len(events),
        relative_delay=relative,
        event_types=_event_types(events),
        critical=stats["min_reading_speed"] < RECOMMENDATION_THRESHOLDS["critical_reading_speed"],
    )
    return _with_interpretation_context(RecommendationView(
        recommendation_id=f"{profile_id}_{step.get('step_id')}_text_structure",
        profile_id=profile_id,
        title="Structure text information more clearly",
        priority=priority,
        finding=(
            f"For the simulated configuration {profile_label} the step "
            f"{_step_label(step)} is notable as a reading or checking step."
        ),
        affected_step=_step_label(step),
        reasoning=(
            "The finding is consistent with a text-related issue because the "
            "affected step involves information intake and the simulation shows "
            "reduced reading speed or additional time."
        ),
        supported_causes=[
            "text volume or information density",
            "several pieces of information that must be processed in parallel",
            "possibly unclear terms or long descriptions",
        ],
        evidence=evidence,
        suggested_actions=[
            "place the most important information at the beginning of the section",
            "shorten descriptive text",
            "add subheadings or visual grouping",
            "make detailed information optionally expandable",
            "briefly explain technical terms",
        ],
        expected_effects=[
            "lower reading demand",
            "shorter completion time",
            "lower cognitive load",
        ],
        affected_metrics=["reading speed", "completion time", "cognitive load"],
        related_events=_event_labels(events),
        usability_principles=["self-descriptiveness", "task suitability"],
        confidence=_confidence(len(evidence), bool(events)),
        source_rule_ids=["reading_step_delay"],
        structured_recommendation=_structured_recommendation(
            step=step,
            events=events,
            fallback_metric_ids=["completion_time", "cognitive_load"],
            cause="text volume, information density or difficult-to-process terms",
            severity="medium" if priority != "high" else "high",
            design_principle="self-descriptiveness",
            general_recommendation=(
                "Shorten and structure textual information and visually "
                "prioritize important content."
            ),
            priority=priority,
            rule_id="reading_step_delay",
        ),
    ))


def _make_attention_recommendation(
    *,
    profile_id: str,
    profile_label: str,
    step: dict,
    rows: list[dict],
    events: list[dict],
) -> RecommendationView:
    planned, actual, relative = _delay_values(step)
    stats = _step_stats(rows)
    evidence = [
        f"lowest attention {stats['min_attention']:.1f} out of 100",
    ]
    if _is_significant_delay(step):
        evidence.append(f"simulated time {actual:.0f} instead of {planned:.0f} seconds")
    if stats["max_error_risk"] >= RECOMMENDATION_THRESHOLDS["notable_error_risk"]:
        evidence.append(f"error risk up to {stats['max_error_risk']:.1f} out of 100")
    if events:
        evidence.append("Events: " + ", ".join(_event_labels(events)))
    priority = _priority(
        event_count=len(events),
        relative_delay=relative,
        event_types=_event_types(events),
        critical=stats["min_attention"] < RECOMMENDATION_THRESHOLDS["critical_attention"],
    )
    return _with_interpretation_context(RecommendationView(
        recommendation_id=f"{profile_id}_{step.get('step_id')}_attention_guidance",
        profile_id=profile_id,
        title="Make orientation and the next action clearer",
        priority=priority,
        finding=(
            f"For the simulated configuration {profile_label}, attention decreases "
            f"notable in step \"{_step_label(step)}\"."
        ),
        affected_step=_step_label(step),
        reasoning=(
            "The recommendation is triggered because this step contains a "
            "notable attention pattern or an attention-related event."
        ),
        supported_causes=[
            "visual competition",
            "unclear continuation",
            "several equally salient action options",
        ],
        evidence=evidence,
        suggested_actions=[
            "visually emphasize the primary next action",
            "reduce competing elements",
            "make the current processing status visible",
            "clearly group related options",
        ],
        expected_effects=[
            "more stable attention",
            "less search effort",
            "lower error risk",
        ],
        affected_metrics=["attention", "error risk", "completion time"],
        related_events=_event_labels(events),
        usability_principles=["controllability", "conformity with expectations"],
        confidence=_confidence(len(evidence), bool(events)),
        source_rule_ids=["attention_drop"],
        structured_recommendation=_structured_recommendation(
            step=step,
            events=events,
            fallback_metric_ids=["error_risk", "completion_time"],
            cause="reduced attention, competing stimuli or unclear continuation",
            severity="medium" if priority != "high" else "high",
            design_principle="conformity with expectations",
            general_recommendation=(
                "Emphasize the next action more clearly and reduce "
                "competing stimuli."
            ),
            priority=priority,
            rule_id="attention_drop",
        ),
    ))


def _make_error_recommendation(
    *,
    profile_id: str,
    profile_label: str,
    step: dict,
    rows: list[dict],
    events: list[dict],
) -> RecommendationView:
    _, _, relative = _delay_values(step)
    stats = _step_stats(rows)
    is_input = _is_input_step(step)
    is_decision = _is_decision_step(step)
    if is_input:
        actions = [
            "clearly mark required fields",
            "validate inputs directly",
            "formulate error messages concretely and actionably",
            "summarize critical inputs before submission",
        ]
        causes = ["uncertain input", "missing feedback", "critical confirmation"]
    elif is_decision:
        actions = [
            "present options in a comparable way",
            "make decision criteria visible",
            "reduce the number of parallel options",
            "clearly explain the consequences of the selection",
        ]
        causes = ["hard-to-compare options", "unclear decision criteria"]
    else:
        actions = [
            "make labels more precise",
            "make selection states visible",
            "show feedback after clicks more clearly",
            "add orientation cues",
        ]
        causes = ["unclear orientation", "uncertain selection", "missing feedback"]
    evidence = [f"error risk up to {stats['max_error_risk']:.1f} out of 100"]
    if events:
        evidence.append("Events: " + ", ".join(_event_labels(events)))
    priority = _priority(
        event_count=len(events),
        relative_delay=relative,
        event_types=_event_types(events),
        critical=stats["max_error_risk"] >= RECOMMENDATION_THRESHOLDS["critical_error_risk"],
    )
    return _with_interpretation_context(RecommendationView(
        recommendation_id=f"{profile_id}_{step.get('step_id')}_error_prevention",
        profile_id=profile_id,
        title="Prevent errors at this point",
        priority=priority,
        finding=(
            f"In step {_step_label(step)} the error risk is notable for "
            f"{profile_label} notable."
        ),
        affected_step=_step_label(step),
        reasoning=_contextual_error_reasoning(
            profile_label=profile_label,
            step=step,
            stats=stats,
            events=events,
        ),
        supported_causes=causes,
        evidence=evidence,
        suggested_actions=actions,
        expected_effects=[
            "fewer incorrect decisions",
            "clearer feedback",
            "higher task success score",
        ],
        affected_metrics=["error risk", "task success score"],
        related_events=_event_labels(events),
        usability_principles=["error tolerance", "self-descriptiveness"],
        confidence=_confidence(len(evidence), bool(events)),
        source_rule_ids=["error_risk"],
        structured_recommendation=_structured_recommendation(
            step=step,
            events=events,
            fallback_metric_ids=["error_risk", "task_success_score"],
            cause=", ".join(causes[:2]),
            severity="medium" if priority != "high" else "high",
            design_principle="error tolerance",
            general_recommendation=(
                "Add error prevention, clear feedback and safe "
                "correction options."
            ),
            priority=priority,
            rule_id="error_risk",
        ),
    ))


def _make_complexity_recommendation(
    *,
    profile_id: str,
    profile_label: str,
    step: dict,
    rows: list[dict],
    events: list[dict],
) -> RecommendationView:
    planned, actual, relative = _delay_values(step)
    stats = _step_stats(rows)
    evidence = [
        f"cognitive load up to {stats['max_cognitive_load']:.1f} out of 100",
    ]
    if _is_significant_delay(step):
        evidence.append(f"simulated time {actual:.0f} instead of {planned:.0f} seconds")
    if events:
        evidence.append("Events: " + ", ".join(_event_labels(events)))
    actions = [
        "divide the step into smaller subtasks",
        "structure information into visible groups",
        "highlight only one primary action per section",
    ]
    if _is_decision_step(step):
        actions.append("show decision criteria directly next to the options")
    priority = _priority(
        event_count=len(events),
        relative_delay=relative,
        event_types=_event_types(events),
        critical=stats["max_cognitive_load"] >= RECOMMENDATION_THRESHOLDS["critical_cognitive_load"],
    )
    return _with_interpretation_context(RecommendationView(
        recommendation_id=f"{profile_id}_{step.get('step_id')}_reduce_complexity",
        profile_id=profile_id,
        title="Simplify and structure the step more clearly",
        priority=priority,
        finding=(
            f"The step {_step_label(step)} produces for {profile_label} "
            "an increased mental load."
        ),
        affected_step=_step_label(step),
        reasoning=(
            "The recommendation is derived from elevated cognitive load, events, "
            "or a relevant time deviation in the same step."
        ),
        supported_causes=[
            "several simultaneous requirements",
            "high decision or memory demand",
            "complex information structure",
        ],
        evidence=evidence,
        suggested_actions=actions,
        expected_effects=[
            "lower cognitive load",
            "more stable task progress",
            "weniger error risk",
        ],
        affected_metrics=["cognitive load", "completion time", "error risk"],
        related_events=_event_labels(events),
        usability_principles=["task suitability", "learnability"],
        confidence=_confidence(len(evidence), bool(events)),
        source_rule_ids=["cognitive_load"],
        structured_recommendation=_structured_recommendation(
            step=step,
            events=events,
            fallback_metric_ids=["cognitive_load", "error_risk"],
            cause="several simultaneous requirements or complex information structure",
            severity="medium" if priority != "high" else "high",
            design_principle="task suitability",
            general_recommendation=(
                "Divide the step into smaller units and reduce parallel "
                "requirements."
            ),
            priority=priority,
            rule_id="cognitive_load",
        ),
    ))


def _make_fallback_recommendation(
    *,
    profile_id: str,
    profile_label: str,
    step: dict,
) -> RecommendationView:
    planned, actual, relative = _delay_values(step)
    return _with_interpretation_context(RecommendationView(
        recommendation_id=f"{profile_id}_{step.get('step_id')}_inspect_step",
        profile_id=profile_id,
        title="Review notable step additionally",
        priority="low",
        finding=(
            f"The step {_step_label(step)} takes {profile_label} "
            f"{actual:.0f} seconds instead of {planned:.0f} seconds."
        ),
        affected_step=_step_label(step),
        reasoning=(
            "Based on the currently recorded data, the time deviation cannot be "
            "clearly attributed to a single factor."
        ),
        supported_causes=["unclear cause"],
        evidence=[f"relative time deviation {relative * 100:.0f} %"],
        suggested_actions=_contextual_fallback_actions(step),
        expected_effects=[
            "clearer next step",
            "less unnecessary search or checking effort",
            "better classification of the cause",
        ],
        affected_metrics=["completion time"],
        confidence="low",
        source_rule_ids=["unattributed_delay"],
        structured_recommendation=_structured_recommendation(
            step=step,
            events=[],
            fallback_metric_ids=["completion_time"],
            cause="time deviation without a clearly attributable single factor",
            severity="low",
            design_principle="task suitability",
            general_recommendation=(
                "Review the step with real users and classify the cause of the "
                "time deviation more precisely."
            ),
            priority="low",
            rule_id="unattributed_delay",
        ),
    ))


def _dedupe_recommendations(
    recommendations: list[RecommendationView],
) -> list[RecommendationView]:
    seen = set()
    deduped = []
    for recommendation in sorted(
        recommendations,
        key=lambda item: {"high": 0, "medium": 1, "low": 2}.get(item.priority, 3),
    ):
        key = (
            recommendation.profile_id,
            recommendation.affected_step,
            recommendation.source_rule_ids[0] if recommendation.source_rule_ids else recommendation.title,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(recommendation)
    return deduped


def build_profile_recommendation_views(
    *,
    profile_id: str,
    profile_label: str,
    timeline: list[dict],
    task_step_durations: list[dict],
    metrics: dict,
    completed: bool = True,
) -> tuple[list[str], list[str], list[dict], list[dict]]:
    rows_by_step = _rows_by_step(timeline)
    recommendations: list[RecommendationView] = []
    problems: list[str] = []

    for step in task_step_durations:
        step_id = str(step.get("step_id") or "")
        rows = rows_by_step.get(step_id, [])
        events = _events_for_rows(rows)
        event_types = _event_types(events)
        stats = _step_stats(rows)
        significant_delay = _is_significant_delay(step)
        has_attention_evidence = (
            "very_low_attention" in event_types
            or stats["min_attention"] < RECOMMENDATION_THRESHOLDS["critical_attention"]
            or (
                profile_id == "adhd"
                and stats["min_attention"] < RECOMMENDATION_THRESHOLDS["notable_attention"]
                and significant_delay
            )
        )
        has_reading_evidence = (
            _is_reading_step(step)
            and (
                stats["min_reading_speed"] < RECOMMENDATION_THRESHOLDS["critical_reading_speed"]
                or (
                    profile_id == "dyslexia"
                    and stats["min_reading_speed"] < RECOMMENDATION_THRESHOLDS["notable_reading_speed"]
                    and significant_delay
                )
            )
        )
        has_error_evidence = (
            "high_error_risk" in event_types
            or "rework_event" in event_types
            or stats["max_error_risk"] >= RECOMMENDATION_THRESHOLDS["notable_error_risk"]
        )
        has_complexity_evidence = (
            "very_high_cognitive_load" in event_types
            or stats["max_cognitive_load"] >= RECOMMENDATION_THRESHOLDS["notable_cognitive_load"]
        )

        if not completed and step.get("status") == "aborted":
            has_complexity_evidence = True

        if has_reading_evidence:
            recommendations.append(
                _make_text_recommendation(
                    profile_id=profile_id,
                    profile_label=profile_label,
                    step=step,
                    rows=rows,
                    events=events,
                )
            )
        if has_attention_evidence:
            recommendations.append(
                _make_attention_recommendation(
                    profile_id=profile_id,
                    profile_label=profile_label,
                    step=step,
                    rows=rows,
                    events=events,
                )
            )
        if has_error_evidence:
            recommendations.append(
                _make_error_recommendation(
                    profile_id=profile_id,
                    profile_label=profile_label,
                    step=step,
                    rows=rows,
                    events=events,
                )
            )
        if has_complexity_evidence:
            recommendations.append(
                _make_complexity_recommendation(
                    profile_id=profile_id,
                    profile_label=profile_label,
                    step=step,
                    rows=rows,
                    events=events,
                )
            )
        if significant_delay and not (
            has_reading_evidence
            or has_attention_evidence
            or has_error_evidence
            or has_complexity_evidence
        ):
            recommendations.append(
                _make_fallback_recommendation(
                    profile_id=profile_id,
                    profile_label=profile_label,
                    step=step,
                )
            )

    recommendation_views = _dedupe_recommendations(recommendations)
    for recommendation in recommendation_views:
        problems.append(recommendation.finding)

    positive_findings = []
    if not recommendation_views:
        event_count = sum(len(row.get("events", [])) for row in timeline)
        completion_efficiency = _metric(metrics, "completion_efficiency")
        task_success = _metric(metrics, "task_success_score")
        finding = (
            f"For {profile_label} no critical patterns were detected."
        )
        evidence = []
        if event_count == 0:
            evidence.append("no notable situations")
        if completion_efficiency >= 65:
            evidence.append(f"completion efficiency {completion_efficiency:.1f} out of 100")
        if task_success >= 65:
            evidence.append(f"task success score {task_success:.1f} out of 100")
        positive_findings.append(
            PositiveFindingView(
                profile_id=profile_id,
                title="Kein dringender Anpassungsbedarf",
                finding=finding,
                evidence=evidence,
            )
        )

    legacy_recommendations = [
        recommendation.title for recommendation in recommendation_views
    ]
    return (
        problems,
        legacy_recommendations,
        [recommendation.model_dump() for recommendation in recommendation_views],
        [finding.model_dump() for finding in positive_findings],
    )
