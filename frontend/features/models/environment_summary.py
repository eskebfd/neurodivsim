import streamlit as st

from frontend.features.models.common import (
    build_live_model_attribute_rows,
    render_model_attribute_summary,
)
from frontend.shared.model_attribute_labels import (
    ENVIRONMENT_ATTRIBUTE_LABELS,
    attribute_items,
)

ENVIRONMENT_ATTRIBUTES = attribute_items(ENVIRONMENT_ATTRIBUTE_LABELS)


def build_environment_attribute_rows(environment_model: dict) -> list[dict]:
    return build_live_model_attribute_rows(
        environment_model,
        ENVIRONMENT_ATTRIBUTES,
    )


def render_environment_model_review(
    environment_model: dict,
    edit_action=None,
) -> dict:
    if not environment_model:
        st.warning("No environment values have been generated yet.")
        return {}

    header_markup = (
        '<div class="cogsim-model-section-header">'
        '<div class="cogsim-model-section-title">'
        "Usage context"
        "</div>"
        '<div class="cogsim-model-section-description">'
        "These values describe external influences such as distraction, "
        "time pressure or interruptions."
        "</div>"
        "</div>"
    )
    if edit_action is not None:
        header_column, action_column = st.columns(
            [0.94, 0.06],
            vertical_alignment="top",
        )
        with header_column:
            st.markdown(header_markup, unsafe_allow_html=True)
        with action_column:
            edit_action()
    else:
        st.markdown(header_markup, unsafe_allow_html=True)

    render_model_attribute_summary(
        title="Current environment values",
        help_text=(
            "These values show which external conditions are included in the "
            "simulation."
        ),
        model=environment_model,
        attributes=ENVIRONMENT_ATTRIBUTES,
    )

    return {}
