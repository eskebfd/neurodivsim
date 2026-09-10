from html import escape

import streamlit as st

from frontend.features.models.common import (
    model_attribute_value,
)
from frontend.features.simulation.utils.helpers import profile_color

USER_ATTRIBUTES = (
    (
        "reading_difficulty",
        "Reading difficulty",
    ),
    (
        "sublexical_decoding_stability",
        "Decoding stability",
    ),
    (
        "orthographic_processing_stability",
        "Orthographic processing stability",
    ),
    (
        "parallel_letter_processing_stability",
        "Parallel letter processing",
    ),
    (
        "attention_stability",
        "Attention stability",
    ),
    (
        "working_memory_stability",
        "Working memory stability",
    ),
    (
        "distraction_sensitivity",
        "Distraction sensitivity",
    ),
    (
        "task_switching_difficulty",
        "Task-switching difficulty",
    ),
    (
        "vigilance_stability",
        "Vigilance stability",
    ),
    (
        "inhibitory_control",
        "Inhibitory control",
    ),
    (
        "attention_switching_stability",
        "Attention-switching stability",
    ),
    (
        "divided_attention_capacity",
        "Divided-attention capacity",
    ),
    (
        "omission_tendency",
        "Omission tendency",
    ),
    (
        "reaction_variability",
        "Reaction variability",
    ),
)


USER_ATTRIBUTE_DESCRIPTIONS = {
    "reading_difficulty": "Describes how strongly reading is modeled as difficult for the configuration.",
    "sublexical_decoding_stability": "Describes how stably individual letters and word parts are recognized.",
    "orthographic_processing_stability": "Describes how stably spellings and word patterns are processed.",
    "parallel_letter_processing_stability": "Describes how well several letters are processed at the same time.",
    "attention_stability": "Describes how well attention is maintained during the task.",
    "working_memory_stability": "Describes how stably information is held in working memory.",
    "distraction_sensitivity": "Describes how strongly external stimuli may interfere with task processing.",
    "task_switching_difficulty": "Describes how demanding switches between subtasks are.",
    "vigilance_stability": "Describes how stable sustained attention remains during longer tasks.",
    "inhibitory_control": "Describes how well irrelevant impulses or distractions are inhibited.",
    "attention_switching_stability": "Describes how stably attention can be redirected deliberately.",
    "divided_attention_capacity": "Describes how well multiple information sources are considered in parallel.",
    "omission_tendency": "Describes how likely content or steps are to be missed.",
    "reaction_variability": "Describes how strongly response speed varies.",
}


USER_MODEL_READONLY_NOTICE = (
    "The profile values are fixed, reproducible reference assumptions and "
    "cannot be changed at this point."
)


def build_user_model_views(
    user_model: dict,
    user_models: dict[str, dict] | None = None,
) -> list[dict]:
    if user_models:
        return [
            {
                "profile_id": profile_id,
                "profile_label": model.get(
                    "user_type",
                    profile_id,
                ),
                "user_model": model,
            }
            for profile_id, model in user_models.items()
        ]

    if user_model:
        return [
            {
                "profile_id": user_model.get(
                    "profile_id",
                    "generic",
                ),
                "profile_label": user_model.get(
                    "user_type",
                    "Generic",
                ),
                "user_model": user_model,
            }
        ]

    return []


def build_user_model_comparison_rows(
    user_model: dict,
    user_models: dict[str, dict] | None = None,
) -> list[dict]:
    profiles = build_user_model_views(
        user_model,
        user_models,
    )

    rows = []

    for attribute_id, label in USER_ATTRIBUTES:
        row = {
            "Attribute-ID": attribute_id,
            "Attribute": label,
            "description": USER_ATTRIBUTE_DESCRIPTIONS.get(attribute_id, ""),
        }

        for profile in profiles:
            row[profile["profile_label"]] = model_attribute_value(
                profile["user_model"].get(attribute_id)
            )

        rows.append(row)

    return rows


def _render_user_model_comparison_cards(
    rows: list[dict],
) -> None:
    cards = []
    for row in rows:
        attribute_label = escape(str(row.get("Attribute", "")))
        attribute_description = escape(str(row.get("description", "")))
        profile_values = []
        profile_index = 0
        for profile_label, value in row.items():
            if profile_label in {"Attribute", "Attribute-ID", "description"}:
                continue
            try:
                numeric_value = max(0.0, min(100.0, float(value)))
            except (TypeError, ValueError):
                numeric_value = 0.0
            color = profile_color(
                {
                    "profile_id": str(profile_label).lower(),
                    "profile_label": str(profile_label),
                },
                profile_index,
            )
            profile_index += 1

            profile_values.append(
                (
                    '<div class="cogsim-user-comparison-value-row">'
                    '<div class="cogsim-user-comparison-value-row__label">'
                    f"<span>{escape(str(profile_label))}</span>"
                    f"<strong>{escape(str(value))}</strong>"
                    "</div>"
                    '<div class="cogsim-user-comparison-value-row__track">'
                    '<span style="'
                    f"width:{numeric_value:.0f}%; background:{escape(color)};"
                    '"></span>'
                    "</div>"
                    "</div>"
                )
            )

        cards.append(
            (
                '<div class="cogsim-user-comparison-card">'
                '<div class="cogsim-user-comparison-card__attribute">'
                f"{attribute_label}"
                "</div>"
                '<p class="cogsim-user-comparison-card__description">'
                f"{attribute_description}"
                "</p>"
                '<div class="cogsim-user-comparison-card__values">'
                f"{''.join(profile_values)}"
                "</div>"
                "</div>"
            )
        )

    st.markdown(
        '<div class="cogsim-user-comparison-grid">'
        + "".join(cards)
        + "</div>",
        unsafe_allow_html=True,
    )


def render_user_model_review(
    user_model: dict,
    user_models: dict[str, dict] | None = None,
) -> dict:
    profile_views = build_user_model_views(
        user_model,
        user_models,
    )

    if not profile_views:
        st.warning("No reference configurations available.")
        return {}

    st.markdown(
        (
            '<div class="cogsim-model-section-header">'
            '<div class="cogsim-model-section-title">'
            "comparison of Reference configurations"
            "</div>"
            '<div class="cogsim-model-section-description">'
            f"{USER_MODEL_READONLY_NOTICE}"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    with st.container(
        key="user_model_comparison",
    ):
        comparison_rows = build_user_model_comparison_rows(
            user_model,
            user_models,
        )
        _render_user_model_comparison_cards(comparison_rows)

    return {}
