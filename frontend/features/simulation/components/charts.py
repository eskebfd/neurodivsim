import streamlit as st

from frontend.features.simulation.components.data import (
    build_event_summary_rows,
    build_metric_chart_rows,
    build_overview_duration_chart_rows,
    build_overview_metric_chart_rows,
    build_task_duration_chart_rows,
    selected_metric_ids_from_session,
)


def render_overview_charts(profiles: list[dict]) -> None:
    metric_rows = build_overview_metric_chart_rows(profiles)
    duration_rows = build_overview_duration_chart_rows(profiles)

    metric_column, duration_column = st.columns(2)
    with metric_column:
        st.markdown("#### Reference configuration comparison")
        st.bar_chart(
            metric_rows,
            x="Reference Configuration",
            y=[
                "Cognitive Load",
                "Error Risk Score",
                "Task Success Score",
                "Completion Efficiency",
            ],
            height=320,
        )

    with duration_column:
        st.markdown("#### Duration and critical events")
        st.bar_chart(
            duration_rows,
            x="Reference Configuration",
            y=["Completion Time (s)", "Events"],
            height=320,
        )


def render_profile_charts(profile: dict) -> None:
    metrics = profile.get("metrics", {})
    metric_rows = build_metric_chart_rows(
        metrics,
        selected_metric_ids_from_session(),
    )
    duration_rows = build_task_duration_chart_rows(profile)
    event_rows = build_event_summary_rows(profile)

    metric_column, event_column = st.columns(2)
    with metric_column:
        st.markdown("#### Result values")
        if metric_rows:
            st.bar_chart(
                metric_rows,
                x="Metric",
                y="Value",
                height=300,
            )
        else:
            st.caption("No result values available.")

    with event_column:
        st.markdown("#### Notable situations")
        if event_rows:
            st.bar_chart(
                event_rows,
                x="Event",
                y="Count",
                height=300,
            )
        else:
            st.caption("No notable situations marked.")

    if duration_rows:
        st.markdown("#### Duration of interaction steps")
        st.bar_chart(
            duration_rows,
            x="Task Step",
            y=["Planned (s)", "Actual (s)", "Delay (s)"],
            height=340,
        )
