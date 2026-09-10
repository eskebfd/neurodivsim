from html import escape

import streamlit as st

from frontend.shared.model_attribute_labels import (
    MODEL_ATTRIBUTE_LABELS,
)

SIGNAL_GROUPS = [
    ("task_signals", "Task"),
    ("interface_signals", "Interface"),
    ("environment_signals", "Environment"),
]

ATTRIBUTE_DEFINITIONS = {
    "task_complexity": "How demanding the task is overall.",
    "number_of_steps": "How many larger interaction steps the task is likely to contain.",
    "reading_demand": "How much text must be read and understood.",
    "input_demand": "How much the person must enter, select or confirm.",
    "memory_demand": "How much information the person must remember during the task.",
    "unfamiliar_word_density": "How many unfamiliar or difficult-to-classify words occur.",
    "orthographic_irregularity": "How strongly spelling and word recognition may make reading more difficult.",
    "morphological_complexity": "How complex word forms and compound terms are.",
    "sustained_attention_demand": "How long the person must maintain attention on the task.",
    "task_switching_demand": "How often the person must switch between steps or information sources.",
    "inhibition_demand": "How strongly irrelevant stimuli or premature actions must be inhibited.",
    "divided_attention_demand": "How strongly several pieces of information must be considered at the same time.",
    "text_volume": "How much text must be read on the interface.",
    "sentence_length": "How long and nested the sentences appear.",
    "word_difficulty": "How difficult the words used in the interface are.",
    "technical_terms": "How many technical terms or specialized labels occur.",
    "visual_clutter": "How dense or visually restless the interface appears.",
    "navigation_complexity": "How difficult it is to find the correct path through the interface.",
    "accessibility_support": "How well the interface supports comprehension and operation.",
    "feedback_quality": "How clearly the interface communicates feedback, errors and status information.",
    "text_legibility": "How legible the text is through size, contrast and presentation.",
    "text_density": "How densely textual information is displayed in limited space.",
    "line_tracking_difficulty": "How difficult it is to track lines and text areas while reading.",
    "stimulus_density": "How many stimuli, options or elements are visible at the same time.",
    "irrelevant_signal_load": "How many distracting or task-irrelevant signals are visible.",
    "feedback_interruptiveness": "How strongly messages, pop-ups or feedback interrupt focus.",
    "focus_guidance": "How clearly the interface guides attention to the next important step.",
    "noise_level": "How loud or disruptive the environment is likely to be.",
    "distractions": "How strongly interruptions or distractions may disrupt the task.",
    "time_pressure": "How strongly time pressure influences task processing.",
    "context_stability": "How stable and predictable the usage context is.",
    "external_interruption_frequency": "How frequently external interruptions can be expected.",
    "attention_recovery_support": "How easily attention can return to the task after a distraction.",
}


def selected_label_for_value(value: int) -> str:
    if value <= 24:
        return "very low"

    if value <= 49:
        return "low to moderate"

    if value <= 74:
        return "Clearly present"

    return "Strongly pronounced"


def build_detected_scenario_context(
    dimensions: dict,
) -> dict:
    task = dimensions.get("primary_task") or (
        dimensions.get("task_options", [{}])[0]
        if dimensions.get("task_options")
        else {}
    )

    environment = (
        dimensions.get("environment_options", [{}])[0]
        if dimensions.get("environment_options")
        else {}
    )

    environment_text = environment.get("label", "")

    if environment.get("description"):
        environment_text += f": {environment['description']}"

    return {
        "device": dimensions.get(
            "detected_device",
            "Laptop",
        ),
        "task": {
            "label": task.get("label", ""),
            "description": task.get(
                "description",
                "",
            ),
        },
        "environment": environment_text,
    }


def definition_for_signal(
    signal: dict,
    attribute: str | None = None,
    fallback: str = (
        "Automatically inferred value for this scenario on a scale from 0 to 100."
    ),
) -> str:
    if attribute and attribute in ATTRIBUTE_DEFINITIONS:
        return ATTRIBUTE_DEFINITIONS[attribute]

    definition = str(signal.get("description") or "").strip()
    return definition or fallback


def _render_dimension_header(
    label: str,
    selected_value: int,
) -> None:
    selected_label = selected_label_for_value(selected_value)

    title_column, value_column, badge_column = st.columns(
        [1, 0.14, 0.36],
        gap="small",
    )

    with title_column:
        st.markdown(
            (
                '<div class="cogsim-dimension-header__title">'
                f"{escape(label)}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with value_column:
        st.markdown(
            (
                '<div class="cogsim-dimension-header__value">'
                f"{selected_value}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with badge_column:
        st.markdown(
            (
                '<div class="cogsim-dimension-header__badge">'
                f"{escape(selected_label)}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def _render_dimension_scale(
    minimum_description: str,
    maximum_description: str,
) -> None:
    st.markdown(
        (
            '<div class="cogsim-dimension-scale">'
            '<span class="cogsim-dimension-scale__minimum">'
            f"{escape(minimum_description)}"
            "</span>"
            '<span class="cogsim-dimension-scale__maximum">'
            f"{escape(maximum_description)}"
            "</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_dimension_info(
    *,
    group_key: str,
    attribute: str,
    label: str,
    definition: str,
    signal: dict,
) -> None:
    with st.popover(
        "Explanation",
        icon=":material/info:",
        use_container_width=False,
        key=f"dimension_info_{group_key}_{attribute}",
    ):
        minimum_description = str(
            signal.get("scale_min_description", "low expression")
        )
        maximum_description = str(
            signal.get("scale_max_description", "high expression")
        )
        rationale = str(signal.get("rationale") or "").strip()

        st.markdown(f"**{label}**")
        st.write(definition)
        st.markdown(
            (
                f"- **Low value:** {minimum_description}\n"
                f"- **High value:** {maximum_description}"
            )
        )
        if rationale:
            st.markdown("**Why was this value inferred?**")
            st.write(rationale)


def _render_dimension_control(
    *,
    group_key: str,
    attribute: str,
    signal: dict,
) -> None:
    label = (
        MODEL_ATTRIBUTE_LABELS.get(attribute)
        or signal.get("name")
        or attribute.replace("_", " ").title()
    )

    current_value = int(signal.get("value", 50))
    slider_key = f"dimension_value_{group_key}_{attribute}"
    display_value = int(st.session_state.get(slider_key, current_value))

    with st.container(
        key=f"dimension_card_{group_key}_{attribute}",
    ):
        _render_dimension_header(
            label,
            display_value,
        )

        selected_value = st.slider(
            label,
            min_value=0,
            max_value=100,
            value=current_value,
            key=slider_key,
            help=signal.get("description") or None,
            label_visibility="collapsed",
        )

        signal["value"] = selected_value
        signal["label"] = selected_label_for_value(selected_value)

        _render_dimension_scale(
            str(
                signal.get(
                    "scale_min_description",
                    "0",
                )
            ),
            str(
                signal.get(
                    "scale_max_description",
                    "100",
                )
            ),
        )

        _render_dimension_info(
            group_key=group_key,
            attribute=attribute,
            label=label,
            definition=definition_for_signal(signal, attribute),
            signal=signal,
        )


def _render_signal_group(
    group_key: str,
    signals: dict,
) -> None:
    if not signals:
        st.caption("No values were inferred for this area.")
        return

    signal_items = list(signals.items())

    left_column, right_column = st.columns(
        2,
        gap="medium",
    )

    for index, (attribute, signal) in enumerate(signal_items):
        target_column = left_column if index % 2 == 0 else right_column

        with target_column:
            _render_dimension_control(
                group_key=group_key,
                attribute=attribute,
                signal=signal,
            )


def render_dimensions_section(
    dimensions: dict,
) -> dict:
    st.markdown(
        (
            '<div class="cogsim-dimensions-intro">'
            '<div class="cogsim-dimensions-intro__title">'
            "Review inferred requirements"
            "</div>"
            '<div class="cogsim-dimensions-intro__text">'
            "Each card describes a property that influences the later simulation. "
            "The scale always ranges from 0 to 100 and is an estimated "
            "attribute value, not a percentage. A value of 0 indicates a very "
            "low expression; 100 indicates a very strong expression. Concrete "
            "scenario information, such as the number of relevant interaction "
            "steps, is also mapped to this value range for modeling."
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    focused_area = st.session_state.get("dimension_focus_area")
    focused_group_key = (
        f"{focused_area}_signals"
        if focused_area in {"task", "interface", "environment"}
        else None
    )
    signal_groups = list(SIGNAL_GROUPS)
    if focused_group_key:
        signal_groups.sort(
            key=lambda item: 0 if item[0] == focused_group_key else 1
        )

    tabs = st.tabs([label for _, label in signal_groups])

    for tab, (group_key, _) in zip(
        tabs,
        signal_groups,
    ):
        signals = dimensions.get(
            group_key,
            {},
        )

        with tab:
            _render_signal_group(
                group_key,
                signals,
            )

    return dimensions
