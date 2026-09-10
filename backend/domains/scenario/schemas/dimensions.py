from pydantic import BaseModel, Field
from typing import List, Literal

from backend.domains.models.schemas.base import DeviceType, ScenarioScope
from backend.domains.scenario.schemas.multimodal import (
    EvidenceSource,
    MultimodalAnalysis,
    ScenarioImageMetadata,
)


class TaskOptionSchema(BaseModel):
    label: str = Field(
        ...,
        description="Short name of the inferred or suggested task.",
    )

    description: str = Field(
        ...,
        description="Kurze Explanation der Task.",
    )

    begründung: str = Field(
        ...,
        description="Rationale for deriving this task from the scenario.",
    )


class EnvironmentOptionSchema(BaseModel):
    label: str = Field(
        ...,
        description="Short name of the environment option.",
    )

    description: str = Field(
        ...,
        description="Kurze Explanation der Environment.",
    )

    relevante_faktoren: List[str] = Field(
        default_factory=list,
        description="Relevant environmental factors for this option.",
    )


class InterfaceContextSchema(BaseModel):
    interface_typ: str = Field(
        ...,
        description="Type of digital system or interface context, such as online shop, form or app area.",
    )

    zentrale_ui_elemente: List[str] = Field(
        default_factory=list,
        description="Central UI elements likely to be relevant in the scenario.",
    )

    interaktionsumfang: ScenarioScope = Field(
        ...,
        description="Assessment of the interaction scope.",
    )

    beschreibung: str = Field(
        ...,
        description="Short description of the interface context.",
    )


class ScenarioAttributeSignalSchema(BaseModel):
    id: str
    name: str
    description: str

    value: int = Field(
        ...,
        ge=0,
        le=100,
        description="Preliminary attribute value based on the scenario.",
    )

    label: str
    scale_min_description: str
    scale_max_description: str
    rationale: str
    confidence: Literal["low", "medium", "high"]
    source: EvidenceSource = Field(
        "text",
        description="Evidence source of the signal.",
    )
    evidence_text: str | None = Field(
        None,
        description="Short note on the specific text or image evidence.",
    )
    uncertainty_notes: List[str] = Field(
        default_factory=list,
        description="Notes on uncertainty or limited observability.",
    )


class TaskDimensionSignalsSchema(BaseModel):
    task_complexity: ScenarioAttributeSignalSchema
    number_of_steps: ScenarioAttributeSignalSchema
    reading_demand: ScenarioAttributeSignalSchema
    input_demand: ScenarioAttributeSignalSchema
    memory_demand: ScenarioAttributeSignalSchema
    unfamiliar_word_density: ScenarioAttributeSignalSchema
    orthographic_irregularity: ScenarioAttributeSignalSchema
    morphological_complexity: ScenarioAttributeSignalSchema
    sustained_attention_demand: ScenarioAttributeSignalSchema
    task_switching_demand: ScenarioAttributeSignalSchema
    inhibition_demand: ScenarioAttributeSignalSchema
    divided_attention_demand: ScenarioAttributeSignalSchema


class InterfaceDimensionSignalsSchema(BaseModel):
    text_volume: ScenarioAttributeSignalSchema
    sentence_length: ScenarioAttributeSignalSchema
    word_difficulty: ScenarioAttributeSignalSchema
    technical_terms: ScenarioAttributeSignalSchema
    visual_clutter: ScenarioAttributeSignalSchema
    navigation_complexity: ScenarioAttributeSignalSchema
    accessibility_support: ScenarioAttributeSignalSchema
    feedback_quality: ScenarioAttributeSignalSchema
    text_legibility: ScenarioAttributeSignalSchema
    text_density: ScenarioAttributeSignalSchema
    line_tracking_difficulty: ScenarioAttributeSignalSchema
    stimulus_density: ScenarioAttributeSignalSchema
    irrelevant_signal_load: ScenarioAttributeSignalSchema
    feedback_interruptiveness: ScenarioAttributeSignalSchema
    focus_guidance: ScenarioAttributeSignalSchema


class EnvironmentDimensionSignalsSchema(BaseModel):
    noise_level: ScenarioAttributeSignalSchema
    distractions: ScenarioAttributeSignalSchema
    time_pressure: ScenarioAttributeSignalSchema
    context_stability: ScenarioAttributeSignalSchema
    external_interruption_frequency: ScenarioAttributeSignalSchema
    attention_recovery_support: ScenarioAttributeSignalSchema


class ScenarioDimensionContextSchema(BaseModel):
    detected_device: DeviceType = Field(
        ...,
        description="Detected or selected device.",
    )

    scenario_summary: str = Field(
        ...,
        description="Short summary of the usage scenario.",
    )

    primary_task: TaskOptionSchema = Field(
        ...,
        description="Primary inferred task that best matches the scenario.",
    )

    interface_context: InterfaceContextSchema = Field(
        ...,
        description="Inferred interface and interaction context.",
    )

    task_options: List[TaskOptionSchema] = Field(
        ...,
        description="Additional plausible task options.",
    )

    environment_options: List[EnvironmentOptionSchema] = Field(
        ...,
        description="Plausible environment options.",
    )

    suggested_metrics: List[str] = Field(
        ...,
        description="Initial suggested metrics for the subsequent simulation.",
    )


class ScenarioDimensionsSchema(BaseModel):
    detected_device: DeviceType = Field(
        ...,
        description="Detected or selected device.",
    )

    scenario_summary: str = Field(
        ...,
        description="Short summary of the usage scenario.",
    )

    primary_task: TaskOptionSchema = Field(
        ...,
        description="Primary inferred task that best matches the scenario.",
    )

    interface_context: InterfaceContextSchema = Field(
        ...,
        description="Inferred interface and interaction context.",
    )

    task_options: List[TaskOptionSchema] = Field(
        ...,
        description="Additional plausible task options.",
    )

    environment_options: List[EnvironmentOptionSchema] = Field(
        ...,
        description="Plausible environment options.",
    )

    suggested_metrics: List[str] = Field(
        ...,
        description="Initial suggested metrics for the subsequent simulation.",
    )

    task_signals: TaskDimensionSignalsSchema = Field(
        ...,
        description="Structured scenario signals for the subsequent task attributes.",
    )

    interface_signals: InterfaceDimensionSignalsSchema = Field(
        ...,
        description="Structured scenario signals for the subsequent interface attributes.",
    )

    environment_signals: EnvironmentDimensionSignalsSchema = Field(
        ...,
        description="Structured scenario signals for the subsequent environment attributes.",
    )

    scenario_image_metadata: ScenarioImageMetadata | None = None
    multimodal_analysis: MultimodalAnalysis | None = None
