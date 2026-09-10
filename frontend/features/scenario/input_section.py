import streamlit as st

from frontend.features.scenario.scenario_form import (
    _render_section_header,
    _render_scenario_text_input,
)


def render_multimodal_summary(
    multimodal_analysis: dict | None,
) -> None:
    if not multimodal_analysis:
        return

    sections = [
        ("Detected from text", "text_signals"),
        ("Detected from image", "image_signals"),
        ("Confirmed by both sources", "confirmed_signals"),
        ("Still unclear", "missing_information"),
        ("Conflicts", "conflicts"),
    ]

    with st.expander(
        "Show inferred information",
        expanded=False,
    ):
        for label, key in sections:
            values = multimodal_analysis.get(key) or []

            if not values:
                continue

            st.markdown(f"**{label}**")

            for value in values:
                st.markdown(f"- {value}")

        warning = multimodal_analysis.get("image_analysis_warning")

        if warning:
            st.warning(warning)


def render_scenario_input_section() -> str:
    _render_section_header(
        icon="file-text",
        title="Describe scenario",
        description=(
            "Capture what the person wants to do, what is visible in the "
            "interface and under which conditions the task is performed."
        ),
    )

    with st.container(key="scenario_text_panel"):
        scenario_description = _render_scenario_text_input()

    st.session_state.scenario_input = scenario_description

    return scenario_description
