import streamlit as st

from frontend.features.models.common import (
    build_live_model_attribute_rows,
    render_model_attribute_summary,
)
from frontend.shared.model_attribute_labels import (
    INTERFACE_ATTRIBUTE_LABELS,
    attribute_items,
)

INTERFACE_ATTRIBUTES = attribute_items(INTERFACE_ATTRIBUTE_LABELS)


def build_interface_attribute_rows(interface_model: dict) -> list[dict]:
    return build_live_model_attribute_rows(
        interface_model,
        INTERFACE_ATTRIBUTES,
    )


def render_interface_model_review(
    interface_model: dict,
    edit_action=None,
) -> dict:
    if not interface_model:
        st.warning("No interface values have been generated yet.")
        return {}

    header_markup = (
        '<div class="cogsim-model-section-header">'
        '<div class="cogsim-model-section-title">'
        "Interface"
        "</div>"
        '<div class="cogsim-model-section-description">'
        "These values describe how clearly structured the interface is, "
        "how much text it contains and how well users are guided "
        "processing."
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
        title="Current interface values",
        help_text=(
            "These values show which interface characteristics are included in the "
            "enter the simulation."
        ),
        model=interface_model,
        attributes=INTERFACE_ATTRIBUTES,
    )

    return {}
