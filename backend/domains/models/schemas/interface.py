from typing import List

from pydantic import BaseModel, Field

from backend.domains.models.schemas.attribute import AttributeValueSchema


def _attribute_default(
    value: int,
    minimum: str,
    maximum: str,
) -> AttributeValueSchema:
    return AttributeValueSchema(
        value=value,
        scale_min_description=minimum,
        scale_max_description=maximum,
        explanation="Compatible default value for older interface model payloads.",
        confidence="medium",
    )


class InterfaceModelSchema(BaseModel):
    text_volume: AttributeValueSchema = Field(
        ...,
        description="Amount of visible or processable text.",
    )

    sentence_length: AttributeValueSchema = Field(
        ...,
        description="Complexity caused by sentence length and text structure.",
    )

    word_difficulty: AttributeValueSchema = Field(
        ...,
        description="Difficulty of the words used.",
    )

    technical_terms: AttributeValueSchema = Field(
        ...,
        description="Share or relevance of technical or domain-specific terms.",
    )

    visual_clutter: AttributeValueSchema = Field(
        ...,
        description="Visual clutter or density of simultaneous elements.",
    )

    navigation_complexity: AttributeValueSchema = Field(
        ...,
        description="Complexity of navigation or orientation in the interface.",
    )

    accessibility_support: AttributeValueSchema = Field(
        ...,
        description="Extent of supportive accessibility or help features.",
    )

    feedback_quality: AttributeValueSchema = Field(
        ...,
        description="Quality of feedback, error messages and status information.",
    )

    text_legibility: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            75,
            "Text is very difficult to read",
            "Text is very easy to read",
        ),
        description="Legibility based on font size, contrast, line height and typographic clarity.",
    )

    text_density: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            35,
            "Very sparse and easy-to-process text structure",
            "Very dense text structure with a high amount of information",
        ),
        description="Density and visual concentration of textual information.",
    )

    line_tracking_difficulty: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            25,
            "Lines and text sections are very easy to follow",
            "Lines and text sections are very difficult to follow",
        ),
        description="Difficulty visually tracking lines or text areas in a stable way.",
    )

    stimulus_density: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            35,
            "Very few simultaneous stimuli",
            "Very many simultaneous visual or interactive stimuli",
        ),
        description="Density of simultaneously visible stimuli, options and interface elements.",
    )

    irrelevant_signal_load: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            25,
            "Hardly any irrelevant signals or distractions",
            "Very many irrelevant signals, banners or competing cues",
        ),
        description="Load caused by irrelevant or competing interface signals.",
    )

    feedback_interruptiveness: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            25,
            "Feedback hardly interrupts focus",
            "Feedback, pop-ups or status cues strongly interrupt focus",
        ),
        description="Extent to which feedback or messages interrupt focus.",
    )

    focus_guidance: AttributeValueSchema = Field(
        default_factory=lambda: _attribute_default(
            65,
            "Interface hardly guides focus",
            "Interface guides focus very clearly to the next step",
        ),
        description="Clarity with which the interface guides attention and the next interaction step.",
    )

    assumptions: List[str] = Field(
        default_factory=list,
        description="Brief assumptions used to derive the interface values.",
    )
