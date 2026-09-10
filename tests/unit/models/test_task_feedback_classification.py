from types import SimpleNamespace

import pytest

from backend.domains.models.schemas.revision_instruction import (
    RevisionInstructionSchema,
    TaskFeedbackClassification,
)
from backend.domains.models.services.model_review import (
    classify_task_feedback_heuristically,
    generate_revision_instruction,
)
from backend.workflow.nodes.review_nodes import prepare_revision_instruction_node


def task_model() -> dict:
    return {
        "steps": [
            {
                "step_id": "step_1",
                "name": "Suche starten",
                "description": "Suchformular absenden",
            },
            {
                "step_id": "step_2",
                "name": "Hotelinformationen lesen",
                "description": "Hotelinformationen review",
            },
            {
                "step_id": "step_3",
                "name": "Hotel select",
                "description": "Passendes Hotel select",
            },
        ]
    }


@pytest.mark.parametrize(
    ("feedback", "expected_type"),
    [
        ("Nach der Suche muss die Person noch Filter select.", "add_step"),
        (
            "Beim Schritt Hotel select sollte vorher noch die Verfügbarkeit geprüft werden.",
            "update_step",
        ),
        ("Der Login-Schritt ist in diesem Scenario nicht notwendig.", "remove_step"),
        (
            "Die Verfügbarkeit muss vor dem comparison of Angebote geprüft werden.",
            "reorder_steps",
        ),
        (
            "Unterkunft select sollte in Angebote vergleichen und Unterkunft select getrennt werden.",
            "split_step",
        ),
        (
            "Reisedaten und Gästeanzahl können als ein gemeinsamer Eingabeschritt behandelt werden.",
            "merge_steps",
        ),
        (
            "Das Lesen der Hotelinformationen dauert deutlich länger.",
            "update_timing",
        ),
        (
            "Beim comparison mehrerer Hotels ist die Gedächtnisanforderung höher.",
            "update_requirements",
        ),
    ],
)
def test_task_feedback_heuristic_classifies_change_types(
    feedback,
    expected_type,
):
    result = classify_task_feedback_heuristically(
        {"hta_feedback": feedback},
        task_model(),
    )

    assert result.change_type == expected_type
    assert result.requested_change == feedback


def test_task_feedback_classification_detects_target_step_name():
    result = classify_task_feedback_heuristically(
        {
            "hta_feedback": (
                "Das Lesen der Hotelinformationen dauert deutlich länger."
            )
        },
        task_model(),
    )

    assert result.change_type == "update_timing"
    assert result.target_step_ids == ["step_2"]
    assert result.target_step_names == ["Hotelinformationen lesen"]


def test_ambiguous_task_feedback_stops_review_node(monkeypatch):
    classification = TaskFeedbackClassification(
        change_type="ambiguous",
        target_step_ids=[],
        target_step_names=[],
        requested_change="Please besser machen.",
        confidence=0.4,
        clarification_question="Was genau soll geändert werden?",
    )

    monkeypatch.setattr(
        "backend.workflow.nodes.review_nodes.generate_revision_instruction",
        lambda **kwargs: RevisionInstructionSchema(
            revision_instruction=(
                "AMBIGUOUS_TASK_FEEDBACK: Keine strukturelle Änderung."
            ),
            task_feedback_classification=classification,
        ),
    )

    result = prepare_revision_instruction_node(
        {
            "scenario_description": "Test scenario",
            "current_stage": "review_base_task",
            "feedback_target": "task_model",
            "feedback": {"hta_feedback": "Please besser machen."},
            "task_model": task_model(),
        }
    )

    assert result["current_stage"] == "finished"
    assert result["task_model"] == task_model()
    assert result["last_feedback"]["task_feedback_classification"][
        "change_type"
    ] == "ambiguous"


def test_generate_revision_instruction_includes_classification(monkeypatch):
    monkeypatch.setattr(
        "backend.domains.models.services.model_review.structured_revision_instruction_model",
        SimpleNamespace(
            invoke=lambda prompt: RevisionInstructionSchema(
                revision_instruction="Aktualisiere die Zeitannahmen."
            )
        ),
    )

    result = generate_revision_instruction(
        scenario_description="Hotelbuchung",
        feedback_target="task_model",
        feedback={
            "hta_feedback": (
                "Das Lesen der Hotelinformationen dauert deutlich länger."
            )
        },
        current_stage="review_base_task",
        current_task_model=task_model(),
    )

    assert result.task_feedback_classification is not None
    assert result.task_feedback_classification.change_type == "update_timing"
    assert "update_timing" in result.revision_instruction
