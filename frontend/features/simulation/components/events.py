from html import escape

import streamlit as st

from frontend.features.simulation.formatting import (
    EVENT_DISPLAY_LABELS,
    task_step_display_label,
)
from frontend.features.simulation.utils.helpers import (
    profile_color,
    step_key,
    step_short_label,
    step_sort_value,
)


def _event_definition_map(presentation: dict | None) -> dict[str, dict]:
    return {
        item.get("event_id"): item
        for item in (presentation or {}).get("event_legend", [])
        if item.get("event_id")
    }


EVENT_TIMELINE_SYMBOLS = {
    "very_high_cognitive_load": "①",
    "high_error_risk": "②",
    "very_low_attention": "③",
    "time_pressure_warning": "④",
    "rework_event": "⑤",
    "task_aborted": "⑥",
    "high_inhibition_load": "⑦",
    "task_switching_strain": "⑧",
}

CIRCLED_EVENT_SYMBOLS = {
    "①": "1",
    "②": "2",
    "③": "3",
    "④": "4",
    "⑤": "5",
    "⑥": "6",
    "⑦": "7",
    "⑧": "8",
}


EVENT_VALUE_UNITS = {
    "high_error_risk": {
        "name": "error risk",
        "kind": "score",
        "direction": "at least",
    },
    "very_high_cognitive_load": {
        "name": "cognitive load",
        "kind": "score",
        "direction": "at least",
    },
    "very_low_attention": {
        "name": "attention",
        "kind": "score",
        "direction": "at most",
    },
    "time_pressure_warning": {
        "name": "remaining time",
        "kind": "percent",
        "direction": "at most",
    },
    "rework_event": {
        "name": "error risk",
        "kind": "score",
        "direction": "at least",
        "context": "in a step with possible correction",
    },
    "task_aborted": {
        "name": "Step duration",
        "kind": "seconds",
        "direction": "at least",
    },
    "high_inhibition_load": {
        "name": "inhibition demand",
        "kind": "score",
        "direction": "at least",
    },
    "task_switching_strain": {
        "name": "switching demand",
        "kind": "score",
        "direction": "at least",
    },
}


def _format_number(value: int | float | str | None) -> str:
    if value in {None, ""}:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}"


def _format_seconds(value: int | float | str | None) -> str:
    if value in {None, ""}:
        return ""
    try:
        total_seconds = max(0, int(round(float(value))))
    except (TypeError, ValueError):
        return str(value)
    minutes, seconds = divmod(total_seconds, 60)
    if minutes:
        return f"{minutes} minutes {seconds} seconds"
    return f"{seconds} seconds"


def _format_event_value(event_type: str, value: int | float | str | None) -> str:
    if value in {None, ""}:
        return ""
    info = EVENT_VALUE_UNITS.get(event_type, {"kind": "score"})
    kind = info.get("kind")
    if kind == "percent":
        return f"{_format_number(value)}% remaining time"
    if kind == "seconds":
        return _format_seconds(value)
    return f"{_format_number(value)} out of 100"


def _format_threshold(event_type: str, threshold: int | float | str | None) -> str:
    if threshold in {None, ""}:
        return ""
    info = EVENT_VALUE_UNITS.get(event_type, {"kind": "score", "direction": "at least"})
    direction = info.get("direction", "at least")
    name = info.get("name", "Value")
    context = info.get("context", "")
    if info.get("kind") == "percent":
        return f"{direction} {_format_number(threshold)}% {name}"
    if info.get("kind") == "seconds":
        return f"{name}: {direction} {_format_seconds(threshold)}"
    suffix = f" {context}" if context else ""
    return f"{name}{suffix}: {direction} {_format_number(threshold)} out of 100"


def build_timeline_event_flag_rows(
    profiles: list[dict],
    presentation: dict | None = None,
) -> list[dict]:
    definitions = _event_definition_map(presentation)
    grouped: dict[tuple[str, str], dict] = {}
    for profile in profiles:
        for item in profile.get("display_timeline", profile.get("timeline", [])):
            task_step = item.get("current_task_step", {})
            for event in item.get("events", []):
                if not isinstance(event, dict):
                    continue
                event_type = event.get("event_type", "event")
                definition = definitions.get(event_type, {})
                key = (step_key(task_step), profile["profile_id"])
                row = grouped.setdefault(
                    key,
                    {
                        "Reference Configuration": profile["profile_label"],
                        "Step": step_short_label(task_step),
                        "Step Detail": task_step_display_label(task_step),
                        "Step Order": step_sort_value(task_step),
                        "Event": "",
                        "Event Labels": [],
                        "Event Details": [],
                        "Event Kurzinfo": [],
                        "Event Explanation": [],
                        "Event Symbols": [],
                        "Event Types": [],
                        "Event Icon Items": [],
                        "Event Count": 0,
                        "Value": 96,
                        "Event Y": 104,
                    },
                )
                event_label = definition.get(
                    "label",
                    EVENT_DISPLAY_LABELS.get(
                        event_type,
                        event_type.replace("_", " ").title(),
                    ),
                )
                symbol = EVENT_TIMELINE_SYMBOLS.get(event_type, "•")
                detail = f"{profile['profile_label']}: {event_label}"
                if detail in row["Event Details"]:
                    continue
                row["Event Details"].append(detail)
                plain_symbol = CIRCLED_EVENT_SYMBOLS.get(symbol, symbol)
                row["Event Kurzinfo"].append(f"{plain_symbol}. {event_label}")
                if event_label not in row["Event Labels"]:
                    row["Event Labels"].append(event_label)
                row["Event Explanation"].append(
                    definition.get(
                        "description",
                        "This event marks a notable situation in the task flow.",
                    )
                )
                if symbol not in row["Event Symbols"]:
                    row["Event Symbols"].append(symbol)
                if event_type not in row["Event Types"]:
                    row["Event Types"].append(event_type)
                    row["Event Icon Items"].append(
                        {
                            "symbol": symbol,
                            "label": event_label,
                            "description": definition.get(
                                "description",
                                "This event marks a notable situation in the task flow.",
                            ),
                        }
                    )
                row["Event Count"] += 1

    rows = []
    for row in grouped.values():
        row["Event"] = " · ".join(row["Event Labels"])
        del row["Event Labels"]
        row["Event Details"] = " · ".join(row["Event Details"])
        row["Event Explanation"] = " · ".join(dict.fromkeys(row["Event Explanation"]))
        row["Event Symbols"] = "\u2003".join(row["Event Symbols"])
        row["Event Kurzinfo"] = "; ".join(row["Event Kurzinfo"])
        row["Event Tooltip"] = (
            f"{row['Event Count']} Event"
            f"{'s' if row['Event Count'] != 1 else ''}: "
            f"{row['Event Kurzinfo']}"
        )
        row["Event Types"] = " · ".join(row["Event Types"])
        rows.append(row)
    return sorted(rows, key=lambda row: (row["Step Order"], row["Reference Configuration"]))


def build_event_icon_legend_items(event_rows: list[dict]) -> list[dict]:
    seen = set()
    items = []
    for row in event_rows:
        for item in row.get("Event Icon Items", []):
            key = (item.get("symbol"), item.get("label"))
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
    return items


def render_event_icon_legend(event_rows: list[dict]) -> None:
    items = build_event_icon_legend_items(event_rows)
    if not items:
        return
    cards = []
    for item in items:
        symbol = str(item.get("symbol") or "•")
        legend_symbol = CIRCLED_EVENT_SYMBOLS.get(symbol, symbol)
        cards.append(
            (
                '<span class="cogsim-event-icon-legend__item">'
                f'<i>{escape(legend_symbol)}</i>'
                f'<b>{escape(str(item.get("label") or "Event"))}</b>'
                "</span>"
            )
        )
    st.markdown(
        (
            '<div class="cogsim-event-icon-legend">'
            '<strong>Event-Marker im Diagramm</strong>'
            f'{"".join(cards)}'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def build_overview_event_legend_rows(profiles: list[dict]) -> list[dict]:
    return build_overview_event_legend_rows_from_definitions(profiles, {})


def build_overview_event_legend_rows_from_definitions(
    profiles: list[dict],
    event_definitions: dict[str, dict],
) -> list[dict]:
    rows = []
    seen = set()
    for profile in profiles:
        for item in profile.get("display_timeline", profile.get("timeline", [])):
            task_step = item.get("current_task_step", {})
            for event in item.get("events", []):
                if not isinstance(event, dict):
                    continue
                event_type = event.get("event_type", "event")
                key = (
                    profile["profile_id"],
                    step_key(task_step),
                    event_type,
                )
                if key in seen:
                    continue
                seen.add(key)
                event_label = EVENT_DISPLAY_LABELS.get(
                    event_type,
                    event_type.replace("_", " ").title(),
                )
                definition = event_definitions.get(event_type, {})
                rows.append(
                    {
                        "profile": profile["profile_label"],
                        "profile_id": profile["profile_id"],
                        "step": step_short_label(task_step),
                        "step_detail": task_step_display_label(task_step),
                        "event": definition.get("label", event_label),
                        "meaning": definition.get(
                            "description",
                            "No backend explanation was provided for this event.",
                        ),
                        "trigger": _format_threshold(
                            event_type,
                            event.get("threshold")
                            or definition.get("trigger_value"),
                        )
                        or definition.get("trigger_description", ""),
                        "value": _format_event_value(
                            event_type,
                            event.get("value"),
                        ),
                        "threshold": _format_threshold(
                            event_type,
                            event.get("threshold")
                            or definition.get("trigger_value"),
                        ),
                        "order": step_sort_value(task_step),
                        "event_type": event_type,
                    }
                )
    return sorted(rows, key=lambda row: (row["profile"], row["order"], row["event"]))


def abort_explanation(profile: dict) -> str:
    step = (
        profile.get("aborted_step_name")
        or profile.get("aborted_step_id")
        or "an interaction step"
    )
    reason = profile.get("abort_reason") or "strain became too high over time"
    if reason == "maximum_duration_exceeded":
        reason_text = (
            "the interaction step took substantially longer than the plausible "
            "processing frame assumed in the simulation"
        )
    else:
        reason_text = str(reason).replace("_", " ")
    return (
        f"The run was aborted at {step} because {reason_text}. "
        "This does not mean that real users would necessarily abandon the task. "
        "It marks an area that may be particularly difficult, long or "
        "frustrating for this configuration."
    )


def _event_type_overview(rows: list[dict]) -> str:
    unique_events = []
    for row in rows:
        if row["event"] not in unique_events:
            unique_events.append(row["event"])
    if not unique_events:
        return "No notable situations detected."
    return " · ".join(escape(event) for event in unique_events)


def _event_cards_for_rows(rows: list[dict]) -> str:
    cards = []
    for row in rows:
        value_markup = (
            '<small><span>Measured value:</span>'
            f'{escape(row["value"])}</small>'
            if row.get("value")
            else ""
        )
        threshold_markup = (
            '<small><span>Threshold:</span>'
            f'{escape(row["threshold"])}</small>'
            if row.get("threshold")
            else (
                '<small><span>Trigger condition</span>'
                f'{escape(row["trigger"])}</small>'
                if row.get("trigger")
                else ""
            )
        )
        cards.append(
            (
                '<article class="cogsim-event-legend-card">'
                '<div class="cogsim-event-legend-card__top">'
                f'<strong>{escape(row["event"])}</strong>'
                "</div>"
                f'<span class="cogsim-event-legend-card__step">{escape(row["step_detail"])}</span>'
                f'<p>{escape(row["meaning"])}</p>'
                '<div class="cogsim-event-legend-card__facts">'
                f"{value_markup}{threshold_markup}"
                "</div>"
                "</article>"
            )
        )
    return "".join(cards)


def _event_step_groups_for_rows(rows: list[dict]) -> str:
    groups: dict[tuple[int, str], list[dict]] = {}
    for row in rows:
        groups.setdefault((row["order"], row["step_detail"]), []).append(row)
    sections = []
    for (_, step_detail), group_rows in sorted(groups.items()):
        step_label = group_rows[0]["step"]
        event_count = len(group_rows)
        sections.append(
            (
                '<section class="cogsim-event-step-group">'
                '<div class="cogsim-event-step-group__header">'
                f'<span>{escape(step_label)}</span>'
                f'<small>{event_count} Event{"s" if event_count != 1 else ""}</small>'
                "</div>"
                '<div class="cogsim-event-legend-grid">'
                f"{_event_cards_for_rows(group_rows)}"
                "</div>"
                "</section>"
            )
        )
    return "".join(sections)


def render_overview_event_legend(
    profiles: list[dict],
    presentation: dict | None = None,
) -> None:
    definitions = _event_definition_map(presentation)
    rows = build_overview_event_legend_rows_from_definitions(
        profiles,
        definitions,
    )
    if not rows:
        st.markdown(
            (
                '<section class="cogsim-event-legend-panel">'
                '<div class="cogsim-result-section-heading">'
                "<span>Triggered events</span>"
                "</div>"
                "</section>"
            ),
            unsafe_allow_html=True,
        )
        return

    profile_sections = []
    for index, profile in enumerate(profiles):
        profile_rows = [
            row for row in rows if row["profile_id"] == profile["profile_id"]
        ]
        color = profile_color(profile, index)
        if profile_rows:
            content = _event_step_groups_for_rows(profile_rows)
        else:
            content = (
                '<p class="cogsim-event-profile-section__empty">'
                "No notable situations were marked for this configuration."
                "</p>"
            )
        profile_sections.append(
            (
                '<section class="cogsim-event-profile-section">'
                '<div class="cogsim-event-profile-section__header">'
                '<span class="cogsim-event-legend-card__dot" '
                f'style="background:{color};"></span>'
                f'<strong>{escape(profile["profile_label"])}</strong>'
                f'<small>{len(profile_rows)} Events</small>'
                "</div>"
                f"{content}"
                "</section>"
            )
        )

    st.markdown(
        (
            '<section class="cogsim-event-legend-panel">'
            '<div class="cogsim-result-section-heading">'
            "<span>Notable situations</span>"
            "<small>Events mark task steps in which a defined threshold was reached or exceeded during the simulation.</small>"
            "</div>"
            '<div class="cogsim-event-intro">'
            "<strong>Was sind Events?</strong>"
            "<p>Events are analytical markers of the simulation. They show "
            "where a configuration reaches a defined threshold during an interaction step.</p>"
            '<span class="cogsim-event-intro__types">'
            f'{_event_type_overview(rows)}'
            "</span>"
            "</div>"
            f"{''.join(profile_sections)}"
            "</section>"
        ),
        unsafe_allow_html=True,
    )


def render_profile_event_legend(
    profile: dict,
    presentation: dict | None = None,
) -> None:
    rows = build_overview_event_legend_rows_from_definitions(
        [profile],
        _event_definition_map(presentation),
    )
    if not rows and profile.get("completed", True):
        st.markdown(
            (
                '<section class="cogsim-event-legend-panel cogsim-event-legend-panel--compact">'
                '<div class="cogsim-result-section-heading">'
                "<span>Notable situations</span>"
                "<small>Events mark task steps in which a defined threshold was reached or exceeded during the simulation. No events were detected for this profile.</small>"
                "</div>"
                "</section>"
            ),
            unsafe_allow_html=True,
        )
        return

    abort_card = ""
    if not profile.get("completed", True):
        abort_card = (
            '<article class="cogsim-event-abort-card">'
            "<strong>Simulation abgebrochen</strong>"
            f'<p>{escape(abort_explanation(profile))}</p>'
            "</article>"
        )

    cards = _event_step_groups_for_rows(rows) if rows else ""
    st.markdown(
        (
            '<section class="cogsim-event-legend-panel cogsim-event-legend-panel--compact">'
            '<div class="cogsim-result-section-heading">'
            "<span>Notable situations</span>"
            "<small>Events mark task steps in which a defined threshold was reached or exceeded during the simulation.</small>"
            "</div>"
            f"{abort_card}"
            f"{cards}"
            "</section>"
        ),
        unsafe_allow_html=True,
    )
