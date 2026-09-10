import streamlit as st

from frontend.features.models import (
    render_environment_model_review,
    render_interface_model_review,
    render_task_attribute_review,
    render_user_model_review,
)

MODEL_TABS = (
    "Task values",
    "Interface",
    "Environment",
    "Reference configurations",
)

SIMULATION_FOUNDATIONS_ACTIVE_TAB_KEY = "simulation_foundations_active_tab"
SIMULATION_FOUNDATIONS_RETURN_TAB_KEY = "simulation_foundations_return_tab"

MODEL_TAB_BY_DIMENSION_AREA = {
    "task": "Task values",
    "interface": "Interface",
    "environment": "Environment",
}


def _render_model_intro() -> None:
    st.markdown(
        (
            '<div class="cogsim-models-intro">'
            '<div class="cogsim-models-intro__title">'
            "Review simulation basis"
            "</div>"
            '<div class="cogsim-models-intro__text">'
            "These values are later combined with the reference configurations. "
            "If something does not fit, the respective section can be edited."
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _go_to_dimension_editor(
    area: str,
) -> None:
    st.session_state.dimension_focus_area = area
    st.session_state[SIMULATION_FOUNDATIONS_RETURN_TAB_KEY] = (
        MODEL_TAB_BY_DIMENSION_AREA.get(area, MODEL_TABS[0])
    )
    st.session_state.return_to_models_after_dimension_edit = True
    st.session_state.simulation_step = 5
    st.rerun()


def _render_dimension_edit_action(
    *,
    area: str,
    label: str,
) -> None:
    if st.button(
        "✎",
        key=f"edit_dimensions_from_{area}",
        type="secondary",
        help=f"Edit {label} in step 5",
    ):
        _go_to_dimension_editor(area)


def _render_task_attribute_tab(
    base_model_preview: dict,
) -> None:
    render_task_attribute_review(
        base_model_preview.get(
            "task_model",
            {},
        ),
        edit_action=lambda: _render_dimension_edit_action(
            area="task",
            label="Task",
        ),
    )


def _render_interface_tab(
    base_model_preview: dict,
) -> None:
    render_interface_model_review(
        base_model_preview.get(
            "interface_model",
            {},
        ),
        edit_action=lambda: _render_dimension_edit_action(
            area="interface",
            label="Interface",
        ),
    )


def _render_environment_tab(
    base_model_preview: dict,
) -> None:
    render_environment_model_review(
        base_model_preview.get(
            "environment_model",
            {},
        ),
        edit_action=lambda: _render_dimension_edit_action(
            area="environment",
            label="Environment",
        ),
    )


def render_simulation_foundations_section() -> None:
    base_model_preview = st.session_state.get("base_model_preview")

    if not base_model_preview:
        st.warning("No simulation basis has been generated yet.")
        return

    if st.session_state.get(SIMULATION_FOUNDATIONS_ACTIVE_TAB_KEY) not in MODEL_TABS:
        st.session_state[SIMULATION_FOUNDATIONS_ACTIVE_TAB_KEY] = MODEL_TABS[0]
    if st.session_state.get(SIMULATION_FOUNDATIONS_RETURN_TAB_KEY) in MODEL_TABS:
        st.session_state[SIMULATION_FOUNDATIONS_ACTIVE_TAB_KEY] = (
            st.session_state.pop(SIMULATION_FOUNDATIONS_RETURN_TAB_KEY)
        )

    with st.container(
        key="models_review",
    ):
        _render_model_intro()

        with st.container(key="models_review_tab_selector"):
            selected_tab = st.radio(
                "Simulation basis area",
                MODEL_TABS,
                key=SIMULATION_FOUNDATIONS_ACTIVE_TAB_KEY,
                horizontal=True,
                label_visibility="collapsed",
            )

        if selected_tab == "Task values":
            _render_task_attribute_tab(base_model_preview)
        elif selected_tab == "Interface":
            _render_interface_tab(base_model_preview)
        elif selected_tab == "Environment":
            _render_environment_tab(base_model_preview)
        else:
            render_user_model_review(
                base_model_preview.get(
                    "user_model",
                    {},
                ),
                base_model_preview.get(
                    "user_models",
                    {},
                ),
            )
