from frontend.features.dimensions.section import (
    SIGNAL_GROUPS,
    build_detected_scenario_context,
    definition_for_signal,
    selected_label_for_value,
)
from frontend.features.user_profiles.section import (
    PROFILE_CARD_CONTENT,
    normalize_user_profiles,
    toggle_user_profile,
)
from frontend.features.evaluation_goals.section import (
    build_metrics_selection,
)
from frontend.features.models.user_profile_summary import USER_MODEL_READONLY_NOTICE


def test_normalize_user_profiles_defaults_to_generic():
    assert normalize_user_profiles([]) == ["Generic"]


def test_normalize_user_profiles_adds_generic_baseline_for_specific_profiles():
    assert normalize_user_profiles(["ADHD"]) == [
        "Generic",
        "ADHD",
    ]


def test_normalize_user_profiles_preserves_adhd_and_dyslexia():
    assert normalize_user_profiles(
        ["ADHD", "Dyslexia"]
    ) == [
        "Generic",
        "ADHD",
        "Dyslexia",
    ]


def test_toggle_user_profile_preserves_multiple_specific_profiles():
    profiles = toggle_user_profile(["Generic"], "ADHD")
    profiles = toggle_user_profile(profiles, "Dyslexia")

    assert profiles == [
        "Generic",
        "ADHD",
        "Dyslexia",
    ]


def test_toggle_user_profile_keeps_generic_baseline_active():
    assert toggle_user_profile(["Generic", "ADHD"], "Generic") == [
        "Generic",
        "ADHD",
    ]


def test_profile_cards_define_professional_metadata_for_each_profile():
    assert set(PROFILE_CARD_CONTENT) == {
        "Generic",
        "ADHD",
        "Dyslexia",
    }
    assert PROFILE_CARD_CONTENT["Generic"]["footer_label"] == "Baseline"
    assert PROFILE_CARD_CONTENT["ADHD"]["footer_label"] == "Select ADHD-informed"
    assert (
        PROFILE_CARD_CONTENT["Dyslexia"]["footer_label"]
        == "Select dyslexia-informed"
    )
    assert all("title" in content for content in PROFILE_CARD_CONTENT.values())
    assert all("description" in content for content in PROFILE_CARD_CONTENT.values())
    assert all("icon" in content for content in PROFILE_CARD_CONTENT.values())


def test_selected_label_for_numeric_dimension_value():
    assert selected_label_for_value(0) == "very low"
    assert selected_label_for_value(49) == "low to moderate"
    assert selected_label_for_value(50) == "Clearly present"
    assert selected_label_for_value(100) == "Strongly pronounced"


def test_dimension_definition_uses_signal_description_or_fallback():
    assert (
        definition_for_signal(
            {"description": "Technischer descriptionstext"},
            "reading_demand",
        )
        == "How much text must be read and understood."
    )
    assert definition_for_signal({"description": "Explanation"}) == "Explanation"
    assert "scale from 0 to 100" in definition_for_signal({})


def test_dimension_tabs_contain_no_user_dimensions():
    assert SIGNAL_GROUPS == [
        ("task_signals", "Task"),
        ("interface_signals", "Interface"),
        ("environment_signals", "Environment"),
    ]


def test_metrics_selection_contains_only_predefined_metrics():
    selection = build_metrics_selection(["cognitive_load", "error_risk"])

    assert [
        metric["metric_id"] for metric in selection["selected_metrics"]
    ] == ["cognitive_load", "error_risk"]
    assert selection["custom_metric_requests"] == []


def test_metrics_selection_can_be_empty_without_default_fallback():
    selection = build_metrics_selection([])

    assert selection == {
        "selected_metrics": [],
        "custom_metric_requests": [],
    }


def test_detected_context_uses_task_device_and_environment_only():
    context = build_detected_scenario_context(
        {
            "detected_device": "Laptop",
            "primary_task": {"label": "Anmelden", "description": "Kurs wählen"},
            "environment_options": [
                {"label": "Arbeitsplatz", "description": "Benachrichtigungen"}
            ],
        }
    )

    assert context == {
        "device": "Laptop",
        "task": {"label": "Anmelden", "description": "Kurs wählen"},
        "environment": "Arbeitsplatz: Benachrichtigungen",
    }


def test_user_model_readonly_notice_explains_locked_profile_values():
    assert "reference assumptions" in USER_MODEL_READONLY_NOTICE
    assert "cannot be changed" in USER_MODEL_READONLY_NOTICE
