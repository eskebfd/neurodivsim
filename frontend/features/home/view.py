import streamlit as st

HOME_STEPS = [
    {
        "number": "01",
        "title": "Describe scenario",
        "description": (
            "Describe the task, the interface and the context in which "
            "the interaction takes place."
        ),
    },
    {
        "number": "02",
        "title": "Inspect models",
        "description": (
            "Review the automatically generated task, interface and "
            "environment models before simulation."
        ),
    },
    {
        "number": "03",
        "title": "Run simulation",
        "description": (
            "Run the deterministic simulation for the selected cognitive "
            "reference configurations."
        ),
    },
    {
        "number": "04",
        "title": "Reflect on results",
        "description": (
            "Compare simulated patterns and derive traceable questions for "
            "design reflection."
        ),
    },
]


def _build_home_hero_html() -> str:
    return (
        '<div class="cogsim-home-hero">'
        '<div class="cogsim-home-eyebrow">NEURODIVSIM</div>'
        '<h1 class="cogsim-home-title">'
        "Reflect on Cognitive Diversity in Interface Design"
        "</h1>"
        '<p class="cogsim-home-lead">'
        "NeuroDivSim supports early design and prototyping by turning "
        "natural-language usage scenarios into inspectable models and "
        "deterministic simulation results."
        "</p>"
        '<p class="cogsim-home-description">'
        "The tool combines task, interface and environment models with "
        "cognitive reference configurations. The resulting metrics, events, "
        "and recommendations are intended as prompts for design reflection, "
        "not as predictions of individual user behavior."
        "</p>"
        "</div>"
    )


def _build_home_step_html(
    number: str,
    title: str,
    description: str,
) -> str:
    return (
        '<div class="cogsim-home-step">'
        f'<div class="cogsim-home-step__number">{number}</div>'
        f'<div class="cogsim-home-step__title">{title}</div>'
        f'<div class="cogsim-home-step__description">{description}</div>'
        "</div>"
    )


def render_home_view() -> None:
    st.html(_build_home_hero_html())

    columns = st.columns(
        len(HOME_STEPS),
        gap="medium",
    )

    for column, step in zip(columns, HOME_STEPS):
        with column:
            st.html(
                _build_home_step_html(
                    number=step["number"],
                    title=step["title"],
                    description=step["description"],
                )
            )

    if st.button(
        "Start new simulation",
        type="primary",
        use_container_width=False,
    ):
        st.session_state.current_view = "simulation"
        st.session_state.simulation_step = 1
        st.rerun()
