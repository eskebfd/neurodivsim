from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowStep:
    number: int
    step_id: str
    label: str
    feature: str
    description: str = ""
    required_state_keys: tuple[str, ...] = ()


USER_PROFILES_STEP = 1
METRICS_STEP = 2
SCENARIO_STEP = 3
TASK_FLOW_STEP = 4
DIMENSIONS_STEP = 5
SIMULATION_FOUNDATIONS_STEP = 6
SIMULATION_PLAN_STEP = 7
RESULTS_STEP = 8


WORKFLOW_STEP_DEFINITIONS = (
    WorkflowStep(
        USER_PROFILES_STEP,
        "user_profiles",
        "Reference configurations",
        "user_profiles",
        "Selection of the cognitive reference configurations to be simulated.",
    ),
    WorkflowStep(
        METRICS_STEP,
        "metrics",
        "Evaluation",
        "evaluation_goals",
        "Selection of the metrics to be examined after the simulation.",
        ("user_profiles",),
    ),
    WorkflowStep(
        SCENARIO_STEP,
        "scenario",
        "Scenario",
        "scenario",
        "Description of the task, interface and usage context.",
        ("evaluation_metrics",),
    ),
    WorkflowStep(
        TASK_FLOW_STEP,
        "task_flow",
        "Interaction flow",
        "task_flow",
        "Generation and inspection of the inferred interaction flow.",
        ("scenario_input",),
    ),
    WorkflowStep(
        DIMENSIONS_STEP,
        "dimensions",
        "Requirements",
        "dimensions",
        "Inspection of the automatically inferred scenario requirements.",
        ("base_model_preview",),
    ),
    WorkflowStep(
        SIMULATION_FOUNDATIONS_STEP,
        "simulation_foundations",
        "Simulation basis",
        "models",
        "Overview of the generated models used by the simulation.",
        ("dimensions", "base_model_preview"),
    ),
    WorkflowStep(
        SIMULATION_PLAN_STEP,
        "simulation_plan",
        "Simulation plan",
        "computed_parameters",
        "Review of computed plan values before running the simulation.",
        ("base_model_preview", "computed_parameters_preview"),
    ),
    WorkflowStep(
        RESULTS_STEP,
        "results",
        "Results",
        "simulation",
        "Comparison of simulation results and design recommendations.",
        ("simulation_result",),
    ),
)


WORKFLOW_STEPS = [
    (step.number, step.label) for step in WORKFLOW_STEP_DEFINITIONS
]


def workflow_step_by_number(step_number: int) -> WorkflowStep | None:
    return next(
        (
            step
            for step in WORKFLOW_STEP_DEFINITIONS
            if step.number == step_number
        ),
        None,
    )
