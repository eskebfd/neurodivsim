from backend.domains.evaluation.registries.metrics import (
    get_predefined_evaluation_metrics,
)
from backend.domains.simulation.config import DEFAULT_SIMULATION_CONFIG
from backend.domains.simulation.events.metric_relations import (
    METRIC_EVENT_RELATIONS,
    event_ids_for_selected_metrics,
)
from backend.domains.simulation.schemas.presentation import (
    CompletionTimeView,
    EventLegendItemView,
    MetricLegendItemView,
    ResultPresentationView,
    ResultSectionDefinitionView,
    ResultSummaryView,
    SummaryItemView,
    SummaryStatusView,
)


METRIC_PRESENTATION = {
    "cognitive_load": {
        "description": (
            "Describes how strongly the simulated configuration is cognitively "
            "strained during task processing."
        ),
        "preferred_direction": "lower is more favorable",
        "influencing_factors": [
            "task complexity",
            "text volume and legibility",
            "navigation effort",
            "memory and decision demands",
            "fatigue over time",
        ],
        "design_context": [
            "structure information more clearly",
            "simplify individual steps",
            "reduce concurrent requirements",
        ],
    },
    "error_risk": {
        "description": (
            "Estimates how likely uncertain decisions, incorrect entries or "
            "necessary repetitions become during task processing."
        ),
        "preferred_direction": "lower is more favorable",
        "influencing_factors": [
            "cognitive load",
            "reduced attention",
            "fatigue",
            "time pressure",
            "unclear inputs or decisions",
        ],
        "design_context": [
            "secure critical inputs",
            "make feedback easier to interpret",
            "explain critical decisions more clearly",
        ],
    },
    "completion_time": {
        "description": (
            "Shows how long a reference configuration requires for the entire "
            "scenario or for an individual step."
        ),
        "preferred_direction": (
            "interpret in relation to the GOMS baseline time or an explicit time limit"
        ),
        "influencing_factors": [
            "GOMS baseline duration",
            "configuration-specific strain",
            "state changes",
            "events and repetitions",
        ],
        "design_context": [
            "prioritize slower steps",
            "reduce unnecessary intermediate actions",
            "make important actions easier to find",
        ],
    },
    "completion_efficiency": {
        "description": (
            "Describes the relation between achieved task progress and the "
            "effort or time required for it."
        ),
        "preferred_direction": "higher is more favorable",
        "influencing_factors": [
            "completion time",
            "attention",
            "reading speed",
            "task success",
        ],
        "design_context": [
            "shorten interaction flows",
            "improve orientation",
            "avoid rework",
        ],
    },
    "task_success_score": {
        "description": (
            "Estimates how likely the reference configuration can complete the "
            "scenario without an abort condition."
        ),
        "preferred_direction": "higher is more favorable",
        "influencing_factors": [
            "error risk",
            "cognitive load",
            "navigation effort",
            "abort and rework events",
        ],
        "design_context": [
            "simplify critical steps",
            "add error prevention",
            "make task completion more explicit",
        ],
    },
    "time_limit_risk": {
        "description": (
            "Indicates a time-related risk only when the scenario contains an "
            "external time limit."
        ),
        "preferred_direction": "lower is more favorable",
        "influencing_factors": [
            "simulated completion time",
            "external time limit",
            "remaining amount of work",
        ],
        "design_context": [
            "review time limits",
            "shorten the task",
            "prioritize intermediate steps",
        ],
    },
}

EVENT_PRESENTATION = {
    "high_error_risk": {
        "label": "Elevated error risk",
        "description": (
            "The calculated error risk reached or exceeded the defined threshold."
        ),
        "trigger": "error risk >= {threshold}",
        "state_changes": ["attention may decrease", "fatigue may increase"],
        "related_metrics": [
            "error risk",
            "completion time",
            "task success score",
            "completion efficiency",
        ],
        "possible_consequences": [
            "uncertain decisions",
            "incorrect entries",
            "repetitions",
        ],
        "design_context": [
            "improve feedback",
            "simplify inputs",
            "add error prevention",
        ],
    },
    "very_high_cognitive_load": {
        "label": "Very high cognitive load",
        "description": (
            "The simulated mental demand reached a critical range."
        ),
        "trigger": "cognitive load >= {threshold}",
        "state_changes": ["fatigue increases"],
        "related_metrics": [
            "cognitive load",
            "error risk",
            "completion time",
            "task success score",
        ],
        "possible_consequences": [
            "slower processing",
            "higher error risk",
            "faster fatigue increase",
        ],
        "design_context": [
            "reduce content density",
            "simplify steps",
            "group information more clearly",
        ],
    },
    "very_low_attention": {
        "label": "Strongly reduced attention",
        "description": (
            "The simulated attention value fell below the defined threshold."
        ),
        "trigger": "attention <= {threshold}",
        "state_changes": ["attention decreases further"],
        "related_metrics": [
            "error risk",
            "completion time",
            "task success score",
        ],
        "possible_consequences": [
            "important cues may be missed",
            "next steps may be harder to find",
            "rework may become more likely",
        ],
        "design_context": [
            "reduce distractions",
            "highlight important content",
            "provide orientation cues",
        ],
    },
    "time_pressure_warning": {
        "label": "Critical time pressure",
        "description": (
            "The remaining time is critical in relation to the remaining amount of work."
        ),
        "trigger": "remaining time <= {threshold} %",
        "state_changes": [
            "attention decreases",
            "fatigue increases",
        ],
        "related_metrics": [
            "time limit risk",
            "error risk",
            "completion time",
        ],
        "possible_consequences": [
            "faster but less certain decisions",
            "higher error risk",
        ],
        "design_context": [
            "review the time limit",
            "shorten the task",
            "enable intermediate saving states",
        ],
    },
    "rework_event": {
        "label": "Step required rework",
        "description": (
            "A previously processed step was repeated because of a simulated "
            "error or elevated error risk."
        ),
        "trigger": "error risk in a rework-capable step >= {threshold}",
        "state_changes": [
            "additional completion time",
            "fatigue increases",
        ],
        "related_metrics": [
            "completion time",
            "completion efficiency",
            "task success score",
        ],
        "possible_consequences": [
            "longer completion time",
            "higher strain",
            "lower efficiency",
        ],
        "design_context": [
            "show errors early",
            "make corrections easy to understand",
            "summarize critical inputs",
        ],
    },
    "task_aborted": {
        "label": "Task aborted",
        "description": (
            "The simulated reference configuration did not complete the task because "
            "a defined abort condition was reached."
        ),
        "trigger": "step duration >= maximum allowed step duration",
        "state_changes": ["simulation ends for this configuration"],
        "related_metrics": [
            "task success score",
            "completion time",
            "completion efficiency",
        ],
        "possible_consequences": [
            "task is not completed",
            "step is particularly critical for the configuration",
        ],
        "design_context": [
            "simplify the critical step",
            "provide additional support",
            "reduce scope",
        ],
    },
    "high_inhibition_load": {
        "label": "High inhibition demand",
        "description": (
            "The task strongly requires suppressing irrelevant stimuli or action impulses."
        ),
        "trigger": "inhibition demand >= {threshold}",
        "state_changes": ["attention decreases slightly", "fatigue increases slightly"],
        "related_metrics": ["error risk", "cognitive load"],
        "possible_consequences": [
            "distractions become more demanding",
            "incorrect clicks become more plausible",
        ],
        "design_context": [
            "reduce visual stimuli",
            "prioritize primary actions more clearly",
        ],
    },
    "task_switching_strain": {
        "label": "Demanding task switching",
        "description": (
            "The step requires demanding switching between information or action options."
        ),
        "trigger": "switching demand >= {threshold} in a switching-related step",
        "state_changes": ["attention decreases slightly", "fatigue increases"],
        "related_metrics": [
            "cognitive load",
            "error risk",
            "completion time",
        ],
        "possible_consequences": [
            "orientation may be lost more easily",
            "comparisons may take longer",
        ],
        "design_context": [
            "present comparison information side by side",
            "make the step sequence clearer",
        ],
    },
}

SECTION_DEFINITIONS = {
    "profile_comparison": ResultSectionDefinitionView(
        section_id="profile_comparison",
        title="Metrics across reference configurations",
        short_explanation=(
            "Metrics summarize central simulation results. The comparison shows "
            "how cognitive load, error risk, completion time and task success "
            "differ across the selected reference configurations."
        ),
        icon_id="bar-chart-3",
    ),
    "interpretation": ResultSectionDefinitionView(
        section_id="interpretation",
        title="Interpreting the result",
        short_explanation=(
            "This section translates the simulation into traceable next steps: "
            "first concrete design recommendations, followed by brief explanations "
            "of metrics and events."
        ),
        icon_id="lightbulb",
    ),
    "timeline": ResultSectionDefinitionView(
        section_id="timeline",
        title="Development over the task",
        short_explanation=(
            "The timeline shows how a selected value changes across interaction "
            "steps. This makes visible when a reference configuration is under "
            "particular strain."
        ),
        icon_id="activity",
    ),
    "events": ResultSectionDefinitionView(
        section_id="events",
        title="Triggered events",
        short_explanation=(
            "Events mark notable situations that emerged during individual "
            "interaction steps. They help explain when and why the simulated state "
            "of a reference configuration changed."
        ),
        icon_id="alert-triangle",
    ),
    "recommendations": ResultSectionDefinitionView(
        section_id="recommendations",
        title="Design recommendations",
        short_explanation=(
            "Design recommendations translate notable simulation patterns into "
            "concrete design considerations. They indicate which step is affected, "
            "which evidence supports the issue and what should be reviewed."
        ),
        icon_id="lightbulb",
    ),
    "metric_legend": ResultSectionDefinitionView(
        section_id="metric_legend",
        title="Metric legend",
        short_explanation=(
            "The legend explains the metrics, their preferred direction and the "
            "design aspects they may inform."
        ),
        icon_id="info",
    ),
    "event_legend": ResultSectionDefinitionView(
        section_id="event_legend",
        title="Event legend",
        short_explanation=(
            "The event legend explains when notable situations are marked and which "
            "metrics or states they affect."
        ),
        icon_id="flag",
    ),
}

def _format_seconds(seconds: float) -> str:
    seconds = max(0, round(float(seconds)))
    minutes, rest = divmod(seconds, 60)
    if minutes:
        return f"{minutes} min {rest} s"
    return f"{rest} s"


def _metric_value(profile: dict, metric_id: str) -> float:
    metrics = profile.get("metrics") or profile.get("final_metrics") or {}
    if metric_id == "completion_time":
        return float(profile.get("completion_time_seconds") or 0)
    return float(metrics.get(metric_id, 0) or 0)


def _goms_basis_seconds(profile: dict) -> float:
    return sum(
        float(step.get("planned_duration_seconds") or 0)
        for step in profile.get("task_step_durations", [])
    )


def _event_count(profile: dict) -> int:
    display_events = profile.get("display_events")
    if display_events is not None:
        return len(display_events)
    return len(profile.get("events", [])) or sum(
        len(item.get("events", [])) for item in profile.get("timeline", [])
    )


def _summary_status(profiles: list[dict]) -> SummaryStatusView:
    if any(not profile.get("completed", True) for profile in profiles):
        return SummaryStatusView(
            status_id="aborted",
            label="Simulation aborted early",
            explanation=(
                "At least one simulated reference configuration could not complete "
                "the scenario. The affected step should be reviewed with priority."
            ),
            severity="danger",
            icon_id="x-circle",
        )
    high_recommendations = sum(
        1
        for profile in profiles
        for card in profile.get("recommendation_cards", [])
        if card.get("priority") == "high"
    )
    total_events = sum(_event_count(profile) for profile in profiles)
    if high_recommendations:
        return SummaryStatusView(
            status_id="critical",
            label="Simulation completed with critical findings",
            explanation=(
                "All simulated configurations could process the scenario. "
                "Some results nevertheless indicate prioritized design issues."
            ),
            severity="warning",
            icon_id="alert-triangle",
            details=f"{high_recommendations} high-priority recommendation(s)",
        )
    if total_events:
        return SummaryStatusView(
            status_id="completed_with_findings",
            label="Simulation completed with findings",
            explanation=(
                "All selected reference configurations could complete the scenario. "
                "However, notable events were detected during processing."
            ),
            severity="notice",
            icon_id="check-circle",
            details=f"{total_events} notable events detected",
        )
    return SummaryStatusView(
        status_id="completed_clear",
        label="Simulation completed successfully",
        explanation=(
            "All selected reference configurations could complete the scenario. "
            "No notable situations were marked."
        ),
        severity="success",
        icon_id="check-circle",
    )


def _task_success_interpretation(value: float) -> str:
    if value >= 75:
        return "high likelihood of completion"
    if value >= 50:
        return "medium likelihood of completion"
    return "low likelihood of completion"


def _build_summary(profiles: list[dict]) -> ResultSummaryView:
    slowest_profile = max(
        profiles,
        key=lambda profile: profile.get("completion_time_seconds") or 0,
    )
    completion_seconds = float(slowest_profile.get("completion_time_seconds") or 0)
    goms_seconds = _goms_basis_seconds(slowest_profile)
    deviation = completion_seconds - goms_seconds
    deviation_percent = (deviation / goms_seconds * 100) if goms_seconds else 0
    profile_names = ", ".join(profile["profile_label"] for profile in profiles)
    total_events = sum(_event_count(profile) for profile in profiles)
    min_success_profile = min(
        profiles,
        key=lambda profile: _metric_value(profile, "task_success_score"),
    )
    min_success = _metric_value(min_success_profile, "task_success_score")

    return ResultSummaryView(
        status=_summary_status(profiles),
        primary_completion_time=CompletionTimeView(
            label="Simulated completion time",
            value_seconds=completion_seconds,
            value_label=_format_seconds(completion_seconds),
            basis_label=(
                "longest simulated completion time "
                f"({slowest_profile['profile_label']})"
            ),
            goms_basis_seconds=goms_seconds,
            goms_basis_label=_format_seconds(goms_seconds),
            deviation_seconds=deviation,
            deviation_label=(
                f"{deviation:+.0f} s or {deviation_percent:+.0f} %"
            ),
            explanation=(
                "The baseline time describes the expected processing duration "
                "under favorable conditions. The simulation additionally considers "
                "configuration-specific strain, state changes, events and possible repetitions."
            ),
            icon_id="clock",
        ),
        secondary_items=[
            SummaryItemView(
                item_id="profiles",
                label=f"{len(profiles)} reference configurations compared",
                value=str(len(profiles)),
                interpretation=profile_names,
                explanation=(
                    "The scenario was simulated with the selected configurations "
                    "so that differences in processing become visible."
                ),
                icon_id="users",
            ),
            SummaryItemView(
                item_id="task_success",
                label="Successful task completion",
                value=f"{min_success:.0f} out of 100",
                interpretation=(
                    f"{_task_success_interpretation(min_success)} "
                    f"for {min_success_profile['profile_label']}"
                ),
                explanation=(
                    "This value describes how likely the model considers complete "
                    "scenario processing without an abort condition. A higher value "
                    "is more favorable."
                ),
                icon_id="target",
                direction="higher is more favorable",
            ),
            SummaryItemView(
                item_id="events",
                label=f"{total_events} notable events detected",
                value=str(total_events),
                interpretation=(
                    "no notable events"
                    if total_events == 0
                    else "notable situations in the task flow"
                ),
                explanation=(
                    "Events mark notable situations within the simulation, for example "
                    "strongly decreasing attention, high cognitive load or repeated "
                    "processing of a step."
                ),
                icon_id="flag",
                direction="fewer is more favorable",
            ),
        ],
        explanation=(
            "The summary first indicates whether the simulation was completed "
            "and which completion time is used as the representative comparison value."
        ),
    )


def _metric_legend_items(
    selected_metric_ids: set[str] | None = None,
) -> list[MetricLegendItemView]:
    items = []
    for metric in get_predefined_evaluation_metrics():
        if (
            selected_metric_ids is not None
            and metric.metric_id not in selected_metric_ids
        ):
            continue
        presentation = METRIC_PRESENTATION.get(metric.metric_id)
        if not presentation:
            continue
        value_range = metric.expected_output_range or (0, 100)
        items.append(
            MetricLegendItemView(
                metric_id=metric.metric_id,
                label=metric.name,
                description=presentation["description"],
                value_range=f"{value_range[0]} to {value_range[1]}",
                unit="seconds" if metric.metric_type == "time" else "points",
                preferred_direction=presentation["preferred_direction"],
                interpretation_ranges=[
                    "0–24: very low",
                    "25–49: low to moderate",
                    "50–74: clearly present",
                    "75–100: strongly pronounced",
                ]
                if metric.metric_type != "time"
                else [
                    "Time values are interpreted in relation to the GOMS baseline time "
                    "or an explicit time limit."
                ],
                influencing_factors=presentation["influencing_factors"],
                related_events=[
                    EVENT_PRESENTATION[event_id]["label"]
                    for event_id in METRIC_EVENT_RELATIONS.get(metric.metric_id, [])
                    if event_id in EVENT_PRESENTATION
                ],
                design_context=presentation["design_context"],
            )
        )
    return items


def _event_legend_items(
    *,
    include_time_pressure: bool,
    selected_metric_ids: set[str] | None = None,
) -> list[EventLegendItemView]:
    thresholds = DEFAULT_SIMULATION_CONFIG.event_thresholds
    allowd_event_ids = event_ids_for_selected_metrics(selected_metric_ids)
    items = []
    for event_id, presentation in EVENT_PRESENTATION.items():
        if allowd_event_ids is not None and event_id not in allowd_event_ids:
            continue
        if event_id == "time_pressure_warning" and not include_time_pressure:
            continue
        threshold_key = "rework_error_risk" if event_id == "rework_event" else event_id
        threshold = thresholds.get(threshold_key)
        trigger_value = str(threshold) if threshold is not None else "dynamic"
        trigger_description = presentation["trigger"].format(
            threshold=trigger_value
        )
        items.append(
            EventLegendItemView(
                event_id=event_id,
                label=presentation["label"],
                description=presentation["description"],
                trigger_description=trigger_description,
                trigger_value=trigger_value,
                severity="high",
                state_changes=presentation["state_changes"],
                related_metrics=presentation["related_metrics"],
                possible_consequences=presentation["possible_consequences"],
                design_context=presentation["design_context"],
            )
        )
    return items


def build_result_presentation_view(
    profile_results: list[dict],
    selected_metric_ids: set[str] | None = None,
) -> dict:
    include_time_pressure = any(
        profile.get("time_limit_seconds") is not None
        or any(
            event.get("event_type") == "time_pressure_warning"
            for event in profile.get("events", [])
        )
        for profile in profile_results
    )
    presentation = ResultPresentationView(
        summary=_build_summary(profile_results),
        sections=SECTION_DEFINITIONS,
        metric_legend=_metric_legend_items(selected_metric_ids),
        event_legend=_event_legend_items(
            include_time_pressure=include_time_pressure,
            selected_metric_ids=selected_metric_ids,
        ),
    )
    return presentation.model_dump()
