from typing import Literal

from pydantic import BaseModel, Field


TaskFeedbackChangeType = Literal[
    "add_step",
    "update_step",
    "remove_step",
    "reorder_steps",
    "split_step",
    "merge_steps",
    "update_timing",
    "update_requirements",
    "ambiguous",
]


class TaskFeedbackClassification(BaseModel):
    change_type: TaskFeedbackChangeType
    target_step_ids: list[str] = Field(default_factory=list)
    target_step_names: list[str] = Field(default_factory=list)
    requested_change: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    clarification_question: str | None = None


class RevisionInstructionSchema(BaseModel):
    revision_instruction: str = Field(
        description=(
            "Clear instruction for the next modeling step. "
            "The instruction describes which model is to be revised "
            "and how the feedback must be incorporated."
        )
    )
    task_feedback_classification: TaskFeedbackClassification | None = None
