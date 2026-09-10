from backend.domains.planning.schemas.simulation_plan import UserProfileSelection
from backend.domains.planning.schemas.simulation_plan import SimulationPlanSchema
from backend.domains.models.schemas.attribute import AttributeValueSchema
from backend.domains.users.registry import (
    get_baseline_user_profile_id,
    get_user_profile,
    list_user_profiles,
    require_user_profile,
    validate_user_profile_ids,
)
from backend.domains.users.schemas.user_model import ProfiledUserModelSchema, UserModelSchema
from backend.domains.users.schemas.profile_definition import UserProfileDefinition


_ATTRIBUTE_SCALE_DESCRIPTIONS = {
    "reading_difficulty": (
        "No reading difficulty",
        "Very strong reading difficulty",
    ),
    "sublexical_decoding_stability": (
        "Grapheme-phoneme mapping is very unstable",
        "Grapheme-phoneme mapping remains very stable",
    ),
    "orthographic_processing_stability": (
        "Orthographic word processing is very unstable",
        "Orthographic word processing remains very stable",
    ),
    "parallel_letter_processing_stability": (
        "Several letters are hardly processed in parallel",
        "Several letters are processed very stably in parallel",
    ),
    "attention_stability": (
        "Attention is very unstable",
        "Attention remains very stable",
    ),
    "distraction_sensitivity": (
        "Hardly sensitive to distractions",
        "Very sensitive to distractions",
    ),
    "task_switching_difficulty": (
        "Task switching is very easy",
        "Task switching is very difficult",
    ),
    "vigilance_stability": (
        "Sustained attention declines very quickly",
        "Sustained attention remains very stable",
    ),
    "inhibitory_control": (
        "Inappropriate responses are hardly inhibited",
        "Inappropriate responses are inhibited very stably",
    ),
    "attention_switching_stability": (
        "Attention switching is very unstable",
        "Attention switching remains very stable",
    ),
    "divided_attention_capacity": (
        "Several information sources can hardly be considered in parallel",
        "Several information sources can be considered very well in parallel",
    ),
    "omission_tendency": (
        "Very low tendency to miss relevant cues",
        "Very high tendency to miss relevant cues or steps",
    ),
    "reaction_variability": (
        "Responses are very consistent",
        "Responses vary strongly",
    ),
    "working_memory_stability": (
        "Working memory is very unstable",
        "Working memory remains very stable",
    ),
}

_PROFILE_ASSUMPTIONS = {
    "generic": ["Generic comparison configuration without a specific cognitive emphasis."],
    "adhd": [
        "ADHD-informed reference configuration with increased distraction sensitivity and reduced sustained attention, inhibition and attention-switching stability."
    ],
    "dyslexia": [
        "Dyslexia-informed reference configuration with increased reading difficulty and reduced decoding, orthographic and parallel letter-processing stability."
    ],
}


def get_available_user_profiles() -> list[UserProfileDefinition]:
    return list_user_profiles()


def get_user_profile_by_id(profile_id: str) -> UserProfileDefinition | None:
    return get_user_profile(profile_id)


def build_user_profile_selections(
    profile_ids: list[str] | None = None,
) -> list[UserProfileSelection]:
    baseline_profile_id = get_baseline_user_profile_id()
    selected_ids = list(dict.fromkeys(profile_ids or [baseline_profile_id]))
    validate_user_profile_ids(selected_ids)
    if baseline_profile_id not in selected_ids:
        selected_ids.insert(0, baseline_profile_id)

    selections = []
    for profile_id in selected_ids:
        profile = require_user_profile(profile_id)
        selections.append(
            UserProfileSelection(
                profile_id=profile.profile_id,
                label=profile.label,
                is_baseline=profile.is_baseline,
            )
        )
    return selections


def build_user_model_from_profile(profile_id: str) -> UserModelSchema:
    profile = require_user_profile(profile_id)

    attributes = {}
    for attribute_id, profile_attribute in profile.attributes.items():
        minimum, maximum = _ATTRIBUTE_SCALE_DESCRIPTIONS[attribute_id]
        attributes[attribute_id] = AttributeValueSchema(
            value=round(profile_attribute.value),
            scale_min_description=minimum,
            scale_max_description=maximum,
            explanation=(
                f"Fixed registry value for the configuration {profile.label}."
            ),
            confidence="high",
        )

    return UserModelSchema(
        user_type=profile.label,
        **attributes,
        assumptions=list(_PROFILE_ASSUMPTIONS[profile.profile_id]),
    )


def generate_user_models_for_plan(
    simulation_plan: SimulationPlanSchema | None,
    **_ignored,
) -> dict[str, ProfiledUserModelSchema]:
    selections = (
        simulation_plan.selected_user_profiles
        if simulation_plan is not None
        else build_user_profile_selections()
    )
    return {
        selection.profile_id: ProfiledUserModelSchema(
            profile_id=selection.profile_id,
            label=selection.label,
            is_baseline=selection.is_baseline,
            user_model=build_user_model_from_profile(selection.profile_id),
        )
        for selection in selections
    }
