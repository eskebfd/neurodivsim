TASK_ATTRIBUTE_LABELS = {
    "task_complexity": "Task complexity",
    "number_of_steps": "Number of steps",
    "reading_demand": "Reading demand",
    "unfamiliar_word_density": "Unfamiliar words",
    "orthographic_irregularity": "Orthographic demand",
    "morphological_complexity": "Word-form complexity",
    "sustained_attention_demand": "Sustained attention",
    "task_switching_demand": "Task-switching demand",
    "inhibition_demand": "Inhibition demand",
    "divided_attention_demand": "Divided attention",
    "input_demand": "Input demand",
    "memory_demand": "Memory demand",
    "decision_demand": "Decision demand",
    "error_criticality": "Error criticality",
}

INTERFACE_ATTRIBUTE_LABELS = {
    "text_volume": "Text volume",
    "sentence_length": "Sentence length",
    "word_difficulty": "Word difficulty",
    "technical_terms": "Technical terms",
    "visual_clutter": "Visual clutter",
    "navigation_complexity": "Navigation complexity",
    "accessibility_support": "Supportive features",
    "feedback_quality": "Feedback quality",
    "text_legibility": "Text legibility",
    "text_density": "Text density",
    "line_tracking_difficulty": "Line-tracking difficulty",
    "stimulus_density": "Stimulus density",
    "irrelevant_signal_load": "Irrelevant signals",
    "feedback_interruptiveness": "Interruptive feedback",
    "focus_guidance": "Focus guidance",
}

ENVIRONMENT_ATTRIBUTE_LABELS = {
    "noise_level": "Noise level",
    "distractions": "Distractions",
    "time_pressure": "Time pressure",
    "context_stability": "Context stability",
    "visual_distraction": "Visual distraction",
    "interruption_risk": "Interruption risk",
    "social_pressure": "Social pressure",
    "device_constraints": "Device constraints",
    "lighting_quality": "Lighting quality",
    "mobility_context": "Mobility context",
    "external_interruption_frequency": "External interruptions",
    "attention_recovery_support": "Attention recovery support",
}

MODEL_ATTRIBUTE_LABELS = {
    **TASK_ATTRIBUTE_LABELS,
    **INTERFACE_ATTRIBUTE_LABELS,
    **ENVIRONMENT_ATTRIBUTE_LABELS,
}


def attribute_items(labels: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(labels.items())
