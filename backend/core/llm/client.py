import json
import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import APITimeoutError

from backend.domains.scenario.schemas.dimensions import (
    EnvironmentDimensionSignalsSchema,
    InterfaceDimensionSignalsSchema,
    ScenarioDimensionContextSchema,
    ScenarioDimensionsSchema,
    TaskDimensionSignalsSchema,
)
from backend.domains.scenario.schemas.multimodal import (
    ScenarioImageAnalysis,
    ScenarioImagePayload,
    ScreenshotTaskAnalysis,
)
from backend.domains.models.schemas.task import TaskModelSchema
from backend.domains.models.schemas.environment import EnvironmentModelSchema
from backend.domains.models.schemas.interface import InterfaceModelSchema
from backend.domains.simulation.schemas.simulation_model import SimulationModelSchema
from backend.domains.planning.schemas.simulation_plan import SimulationPlanSchema

from backend.core.llm.prompt_loader import load_prompt
from backend.domains.planning.services.computed_parameters import (
    build_computed_task_parameters,
)
from backend.domains.models.services.simulation_models import build_simulation_model
from backend.core.logging.workflow_logging import log_duration, logger
from backend.domains.scenario.services.image_processing import decode_scenario_image
from backend.domains.scenario.services.multimodal_analysis import (
    analyze_scenario_image,
    analyze_screenshot_for_task_structure,
    build_fallback_image_analysis,
    fuse_text_and_image_dimensions,
    log_image_analysis_failure,
)

load_dotenv()


def _llm_client_kwargs() -> dict:
    kwargs = {
        "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
        "temperature": 0,
        "request_timeout": 80,
        "max_retries": 0,
    }

    base_url = os.getenv("LLM_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        kwargs["api_key"] = api_key

    return kwargs


llm = ChatOpenAI(
    **_llm_client_kwargs(),
)


structured_dimensions_model = llm.with_structured_output(
    ScenarioDimensionsSchema,
    include_raw=True,
)
structured_dimension_context_model = llm.with_structured_output(
    ScenarioDimensionContextSchema,
    include_raw=True,
)
structured_task_dimensions_model = llm.with_structured_output(
    TaskDimensionSignalsSchema,
    include_raw=True,
)
structured_interface_dimensions_model = llm.with_structured_output(
    InterfaceDimensionSignalsSchema,
    include_raw=True,
)
structured_environment_dimensions_model = llm.with_structured_output(
    EnvironmentDimensionSignalsSchema,
    include_raw=True,
)
structured_image_analysis_model = llm.with_structured_output(
    ScenarioImageAnalysis,
    include_raw=True,
)
structured_screenshot_task_analysis_model = llm.with_structured_output(
    ScreenshotTaskAnalysis,
    include_raw=True,
)
structured_task_model = llm.with_structured_output(TaskModelSchema, include_raw=True)
structured_environment_model = llm.with_structured_output(
    EnvironmentModelSchema,
    include_raw=True,
)
structured_interface_model = llm.with_structured_output(
    InterfaceModelSchema,
    include_raw=True,
)


class WorkflowLLMTimeoutError(RuntimeError):
    error_type = "APITimeoutError"

    def __init__(self, workflow_step: str, attempts: int):
        self.workflow_step = workflow_step
        super().__init__(
            f"LLM request timed out during '{workflow_step}' after "
            f"{attempts} attempts."
        )


def invoke_structured(
    model,
    prompt: str,
    stage: str,
    timeout_retries: int = 0,
):
    attempts = timeout_retries + 1

    for attempt in range(1, attempts + 1):
        try:
            result = model.invoke(prompt)
            break
        except APITimeoutError as exc:
            logger.warning(
                "LLM_TIMEOUT workflow_step=%s attempt=%s max_attempts=%s",
                stage,
                attempt,
                attempts,
            )
            if attempt == attempts:
                raise WorkflowLLMTimeoutError(stage, attempts) from exc

    if not isinstance(result, dict) or "parsed" not in result:
        return result

    parsing_error = result.get("parsing_error")
    raw = result.get("raw")

    if parsing_error is not None:
        raw_content = getattr(raw, "content", raw)
        logger.error(
            "LLM_PARSING_ERROR stage=%s error=%r raw_response=%r",
            stage,
            parsing_error,
            raw_content,
        )
        raise parsing_error

    parsed = result.get("parsed")
    if parsed is None:
        logger.error(
            "LLM_EMPTY_STRUCTURED_OUTPUT stage=%s raw_response=%r",
            stage,
            getattr(raw, "content", raw),
        )
        raise ValueError(f"LLM returned no parsed output for {stage}.")

    return parsed


def select_dimension_context(
    scenario_dimensions: dict | None,
    signal_key: str,
) -> dict:
    if not scenario_dimensions:
        return {}

    return {
        "scenario_summary": scenario_dimensions.get("scenario_summary", ""),
        "primary_task": scenario_dimensions.get("primary_task", {}),
        "interface_context": scenario_dimensions.get("interface_context", {}),
        "signals": scenario_dimensions.get(signal_key, {}),
    }


def build_simulation_plan_prompt_context(
    simulation_plan: SimulationPlanSchema | None,
) -> str:
    if simulation_plan is None:
        return ""

    summary = {
        "selected_user_profiles": [
            profile.profile_id
            for profile in simulation_plan.selected_user_profiles
        ],
        "evaluation_metrics": [
            metric.metric_id for metric in simulation_plan.evaluation_metrics
        ],
        "required_models": [
            model.model_type for model in simulation_plan.required_models
        ],
        "required_attributes": [
            attribute.attribute_id
            for attribute in simulation_plan.required_attributes
        ],
    }
    return "\n\n" + load_prompt("simulation_plan_context.prompt.txt").format(
        simulation_plan_summary=json.dumps(
            summary,
            ensure_ascii=False,
            sort_keys=True,
        )
    )


def _signal(attribute_id: str, name: str, value: int, rationale: str) -> dict:
    return {
        "id": attribute_id,
        "name": name,
        "description": name,
        "value": value,
        "label": "estimated with uncertainty",
        "scale_min_description": "weakly pronounced",
        "scale_max_description": "strongly pronounced",
        "rationale": rationale,
        "confidence": "low",
        "source": "assumption",
        "evidence_text": rationale,
        "uncertainty_notes": [
            "Only an image is available; use context and the precise task are missing."
        ],
    }


def _image_only_dimensions(
    image_analysis: ScenarioImageAnalysis,
) -> ScenarioDimensionsSchema:
    interface_values = {
        key: signal.value
        for key, signal in image_analysis.interface_signals.items()
        if signal.value is not None and signal.confidence in {"medium", "high"}
    }
    task_values = {
        key: signal.value
        for key, signal in image_analysis.task_signals.items()
        if signal.value is not None and signal.confidence in {"medium", "high"}
    }
    return ScenarioDimensionsSchema.model_validate(
        {
            "detected_device": "Laptop",
            "scenario_summary": (
                "Interface screenshot without sufficient use context. "
                "The analysis is limited to visible interface characteristics."
            ),
            "primary_task": {
                "label": "Unclear visible interface task",
                "description": "The concrete task can only be determined to a limited extent from the image alone.",
                "begründung": "No or hardly any descriptive scenario text was provided.",
            },
            "interface_context": {
                "interface_typ": "Unknown digital interface",
                "zentrale_ui_elemente": image_analysis.image_signals[:5],
                "interaktionsumfang": "unbekannt",
                "beschreibung": "Interface context inferred from a screenshot with limited certainty.",
            },
            "task_options": [],
            "environment_options": [
                {
                    "label": "Not inferable from the screenshot",
                    "description": "Environmental conditions must be described in text.",
                    "relevante_faktoren": [],
                }
            ],
            "suggested_metrics": ["Cognitive Load", "Error Risk"],
            "task_signals": {
                "task_complexity": _signal("task_complexity", "Task Complexity", task_values.get("task_complexity", 50), "Image-only fallback."),
                "number_of_steps": _signal("number_of_steps", "Number Of Steps", task_values.get("number_of_steps", 50), "Image-only fallback."),
                "reading_demand": _signal("reading_demand", "Reading Demand", task_values.get("reading_demand", 50), "Image-only fallback."),
                "input_demand": _signal("input_demand", "Input Demand", task_values.get("input_demand", 50), "Image-only fallback."),
                "memory_demand": _signal("memory_demand", "Memory Demand", 50, "Not reliably inferable from the image."),
                "unfamiliar_word_density": _signal("unfamiliar_word_density", "Unfamiliar Words", task_values.get("unfamiliar_word_density", 50), "Image-only fallback."),
                "orthographic_irregularity": _signal("orthographic_irregularity", "Orthographic Demand", task_values.get("orthographic_irregularity", 50), "Image-only fallback."),
                "morphological_complexity": _signal("morphological_complexity", "Word Form Complexity", task_values.get("morphological_complexity", 50), "Image-only fallback."),
                "sustained_attention_demand": _signal("sustained_attention_demand", "Sustained Attention Demand", task_values.get("sustained_attention_demand", 50), "Image-only fallback."),
                "task_switching_demand": _signal("task_switching_demand", "Switching Demand", task_values.get("task_switching_demand", 50), "Image-only fallback."),
                "inhibition_demand": _signal("inhibition_demand", "Inhibition Demand", task_values.get("inhibition_demand", 50), "Image-only fallback."),
                "divided_attention_demand": _signal("divided_attention_demand", "Divided Attention", task_values.get("divided_attention_demand", 50), "Image-only fallback."),
            },
            "interface_signals": {
                "text_volume": _signal("text_volume", "Text Volume", interface_values.get("text_volume", 50), "Image-only fallback."),
                "sentence_length": _signal("sentence_length", "Sentence Length", interface_values.get("sentence_length", 50), "Image-only fallback."),
                "word_difficulty": _signal("word_difficulty", "Word Difficulty", interface_values.get("word_difficulty", 50), "Image-only fallback."),
                "technical_terms": _signal("technical_terms", "Technical Terms", interface_values.get("technical_terms", 50), "Image-only fallback."),
                "visual_clutter": _signal("visual_clutter", "Visual Clutter", interface_values.get("visual_clutter", 50), "Image-only fallback."),
                "navigation_complexity": _signal("navigation_complexity", "Navigation Complexity", interface_values.get("navigation_complexity", 50), "Image-only fallback."),
                "accessibility_support": _signal("accessibility_support", "Accessibility Support", interface_values.get("accessibility_support", 50), "Image-only fallback."),
                "feedback_quality": _signal("feedback_quality", "Feedback Quality", interface_values.get("feedback_quality", 50), "Image-only fallback."),
                "text_legibility": _signal("text_legibility", "Text Legibility", interface_values.get("text_legibility", 50), "Image-only fallback."),
                "text_density": _signal("text_density", "Text Density", interface_values.get("text_density", 50), "Image-only fallback."),
                "line_tracking_difficulty": _signal("line_tracking_difficulty", "Line Tracking", interface_values.get("line_tracking_difficulty", 50), "Image-only fallback."),
                "stimulus_density": _signal("stimulus_density", "Stimulus Density", interface_values.get("stimulus_density", 50), "Image-only fallback."),
                "irrelevant_signal_load": _signal("irrelevant_signal_load", "Irrelevant Signals", interface_values.get("irrelevant_signal_load", 50), "Image-only fallback."),
                "feedback_interruptiveness": _signal("feedback_interruptiveness", "Interruptive Feedback", interface_values.get("feedback_interruptiveness", 50), "Image-only fallback."),
                "focus_guidance": _signal("focus_guidance", "Focus Guidance", interface_values.get("focus_guidance", 50), "Image-only fallback."),
            },
            "environment_signals": {
                "noise_level": _signal("noise_level", "Noise Level", 50, "Not inferable from the screenshot."),
                "distractions": _signal("distractions", "Distractions", 50, "Not inferable from the screenshot."),
                "time_pressure": _signal("time_pressure", "Time Pressure", 50, "Not inferable from the screenshot."),
                "context_stability": _signal("context_stability", "Context Stability", 50, "Not inferable from the screenshot."),
                "external_interruption_frequency": _signal("external_interruption_frequency", "External Interruptions", 50, "Not inferable from the screenshot."),
                "attention_recovery_support": _signal("attention_recovery_support", "Attention Recovery Support", 50, "Not inferable from the screenshot."),
            },
        }
    )


def _model_to_json(value) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _coerce_dimension_context(parsed) -> ScenarioDimensionContextSchema:
    if isinstance(parsed, ScenarioDimensionsSchema):
        return ScenarioDimensionContextSchema.model_validate(parsed.model_dump())
    return ScenarioDimensionContextSchema.model_validate(parsed)


def _coerce_task_signals(parsed) -> TaskDimensionSignalsSchema:
    if isinstance(parsed, ScenarioDimensionsSchema):
        return parsed.task_signals
    return TaskDimensionSignalsSchema.model_validate(parsed)


def _coerce_interface_signals(parsed) -> InterfaceDimensionSignalsSchema:
    if isinstance(parsed, ScenarioDimensionsSchema):
        return parsed.interface_signals
    return InterfaceDimensionSignalsSchema.model_validate(parsed)


def _coerce_environment_signals(parsed) -> EnvironmentDimensionSignalsSchema:
    if isinstance(parsed, ScenarioDimensionsSchema):
        return parsed.environment_signals
    return EnvironmentDimensionSignalsSchema.model_validate(parsed)


def extract_scenario_dimension_context(
    scenario_description: str,
) -> ScenarioDimensionContextSchema:
    prompt_template = load_prompt("scenario_dimension_context.prompt.txt")
    prompt = prompt_template.format(scenario_description=scenario_description.strip())

    with log_duration(
        "llm.extract_scenario_dimension_context",
        prompt_chars=len(prompt),
    ):
        parsed = invoke_structured(
            structured_dimension_context_model,
            prompt,
            "scenario_dimension_context",
            timeout_retries=1,
        )
    return _coerce_dimension_context(parsed)


def extract_task_dimension_signals(
    scenario_description: str,
    dimension_context: ScenarioDimensionContextSchema | dict,
) -> TaskDimensionSignalsSchema:
    prompt_template = load_prompt("scenario_task_dimensions.prompt.txt")
    prompt = prompt_template.format(
        scenario_description=scenario_description.strip(),
        dimension_context=_model_to_json(dimension_context),
    )

    with log_duration(
        "llm.extract_task_dimension_signals",
        prompt_chars=len(prompt),
    ):
        parsed = invoke_structured(
            structured_task_dimensions_model,
            prompt,
            "scenario_task_dimensions",
            timeout_retries=1,
        )
    return _coerce_task_signals(parsed)


def extract_interface_dimension_signals(
    scenario_description: str,
    dimension_context: ScenarioDimensionContextSchema | dict,
) -> InterfaceDimensionSignalsSchema:
    prompt_template = load_prompt("scenario_interface_dimensions.prompt.txt")
    prompt = prompt_template.format(
        scenario_description=scenario_description.strip(),
        dimension_context=_model_to_json(dimension_context),
    )

    with log_duration(
        "llm.extract_interface_dimension_signals",
        prompt_chars=len(prompt),
    ):
        parsed = invoke_structured(
            structured_interface_dimensions_model,
            prompt,
            "scenario_interface_dimensions",
            timeout_retries=1,
        )
    return _coerce_interface_signals(parsed)


def extract_environment_dimension_signals(
    scenario_description: str,
    dimension_context: ScenarioDimensionContextSchema | dict,
) -> EnvironmentDimensionSignalsSchema:
    prompt_template = load_prompt("scenario_environment_dimensions.prompt.txt")
    prompt = prompt_template.format(
        scenario_description=scenario_description.strip(),
        dimension_context=_model_to_json(dimension_context),
    )

    with log_duration(
        "llm.extract_environment_dimension_signals",
        prompt_chars=len(prompt),
    ):
        parsed = invoke_structured(
            structured_environment_dimensions_model,
            prompt,
            "scenario_environment_dimensions",
            timeout_retries=1,
        )
    return _coerce_environment_signals(parsed)


def merge_scenario_dimension_parts(
    dimension_context: ScenarioDimensionContextSchema | dict,
    task_signals: TaskDimensionSignalsSchema | dict,
    interface_signals: InterfaceDimensionSignalsSchema | dict,
    environment_signals: EnvironmentDimensionSignalsSchema | dict,
) -> ScenarioDimensionsSchema:
    context = _coerce_dimension_context(dimension_context)
    return ScenarioDimensionsSchema.model_validate(
        {
            **context.model_dump(),
            "task_signals": _coerce_task_signals(task_signals).model_dump(),
            "interface_signals": _coerce_interface_signals(
                interface_signals
            ).model_dump(),
            "environment_signals": _coerce_environment_signals(
                environment_signals
            ).model_dump(),
        }
    )


def extract_text_scenario_dimensions_parallel(
    scenario_description: str,
) -> ScenarioDimensionsSchema:
    dimension_context = extract_scenario_dimension_context(scenario_description)

    with ThreadPoolExecutor(max_workers=3) as executor:
        task_future = executor.submit(
            extract_task_dimension_signals,
            scenario_description,
            dimension_context,
        )
        interface_future = executor.submit(
            extract_interface_dimension_signals,
            scenario_description,
            dimension_context,
        )
        environment_future = executor.submit(
            extract_environment_dimension_signals,
            scenario_description,
            dimension_context,
        )

        return merge_scenario_dimension_parts(
            dimension_context,
            task_future.result(),
            interface_future.result(),
            environment_future.result(),
        )


def extract_scenario_dimensions(
    scenario_description: str,
    scenario_image: ScenarioImagePayload | dict | None = None,
) -> ScenarioDimensionsSchema:
    scenario_text = scenario_description.strip()
    if not scenario_text and scenario_image is None:
        raise ValueError("Scenario text or image is required.")

    image_bytes = None
    image_metadata = None
    image_analysis = None
    image_warning = None
    if scenario_image is not None:
        image_bytes, image_metadata = decode_scenario_image(scenario_image)
        try:
            image_analysis = analyze_scenario_image(
                image_bytes=image_bytes,
                metadata=image_metadata,
                scenario_text=scenario_text or None,
                structured_image_model=structured_image_analysis_model,
            )
        except Exception as exc:
            log_image_analysis_failure(exc)
            image_warning = str(exc)
            image_analysis = build_fallback_image_analysis(image_metadata, image_warning)

    if not scenario_text:
        dimensions = _image_only_dimensions(image_analysis)
        return fuse_text_and_image_dimensions(
            dimensions,
            image_analysis,
            image_metadata=image_metadata,
            image_analysis_failed=image_warning is not None,
            image_analysis_warning=image_warning,
        )

    with log_duration(
        "llm.extract_scenario_dimensions",
        analysis_mode="parallel_dimension_parts",
    ):
        dimensions = extract_text_scenario_dimensions_parallel(scenario_text)
    if image_analysis is None:
        return dimensions
    return fuse_text_and_image_dimensions(
        dimensions,
        image_analysis,
        image_metadata=image_metadata,
        image_analysis_failed=image_warning is not None,
        image_analysis_warning=image_warning,
    )


def analyze_screenshot_task_structure(
    scenario_image: ScenarioImagePayload | dict,
) -> ScreenshotTaskAnalysis:
    image_bytes, image_metadata = decode_scenario_image(scenario_image)
    return analyze_screenshot_for_task_structure(
        image_bytes=image_bytes,
        metadata=image_metadata,
        structured_task_analysis_model=structured_screenshot_task_analysis_model,
    )


def generate_task_model(
    scenario_context: dict,
    scenario_dimensions: dict | None = None,
    revision_instruction: str = "",
    simulation_plan: SimulationPlanSchema | None = None,
    current_task_model: dict | None = None,
) -> TaskModelSchema:
    prompt_template = load_prompt("task_model.prompt.txt")

    prompt = prompt_template.format(
        description=scenario_context["description"],
        task=scenario_context["task"],
        scenario_dimensions=select_dimension_context(
            scenario_dimensions,
            "task_signals",
        ),
        revision_instruction=revision_instruction,
    )
    if current_task_model:
        prompt += "\n\n" + load_prompt(
            "current_task_model_revision_context.prompt.txt"
        ).format(
            current_task_model=json.dumps(
                current_task_model,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    prompt += build_simulation_plan_prompt_context(simulation_plan)

    with log_duration(
        "llm.generate_task_model",
        prompt_chars=len(prompt),
    ):
        return invoke_structured(
            structured_task_model,
            prompt,
            "task_model",
            timeout_retries=1,
        )


def generate_environment_model(
    scenario_context: dict,
    scenario_dimensions: dict | None = None,
    revision_instruction: str = "",
    simulation_plan: SimulationPlanSchema | None = None,
) -> EnvironmentModelSchema:
    prompt_template = load_prompt("environment_model.prompt.txt")

    prompt = prompt_template.format(
        description=scenario_context["description"],
        environment=scenario_context["environment"],
        device=scenario_context["device"],
        scenario_dimensions=select_dimension_context(
            scenario_dimensions,
            "environment_signals",
        ),
        revision_instruction=revision_instruction,
    )
    prompt += build_simulation_plan_prompt_context(simulation_plan)

    with log_duration(
        "llm.generate_environment_model",
        prompt_chars=len(prompt),
    ):
        return invoke_structured(
            structured_environment_model,
            prompt,
            "environment_model",
            timeout_retries=1,
        )


def generate_interface_model(
    scenario_context: dict,
    scenario_dimensions: dict | None = None,
    revision_instruction: str = "",
    simulation_plan: SimulationPlanSchema | None = None,
) -> InterfaceModelSchema:
    prompt_template = load_prompt("interface_model.prompt.txt")

    prompt = prompt_template.format(
        description=scenario_context["description"],
        task=scenario_context["task"],
        scenario_dimensions=select_dimension_context(
            scenario_dimensions,
            "interface_signals",
        ),
        revision_instruction=revision_instruction,
    )
    prompt += build_simulation_plan_prompt_context(simulation_plan)

    with log_duration(
        "llm.generate_interface_model",
        prompt_chars=len(prompt),
    ):
        return invoke_structured(
            structured_interface_model,
            prompt,
            "interface_model",
            timeout_retries=1,
        )


def generate_simulation_model(
    scenario_context: dict,
    user_model: dict,
    task_model: dict,
    interface_model: dict,
    environment_model: dict,
    revision_instruction: str = "",
) -> SimulationModelSchema:
    with log_duration(
        "service.generate_simulation_model",
    ):
        return build_simulation_model(user_model)
