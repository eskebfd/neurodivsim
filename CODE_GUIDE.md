# CODE_GUIDE

## 1. Purpose of this document

This file provides a compact orientation for the NeuroDivSim source code. It complements the `README.md`, which explains installation and startup, by describing the structure of the implementation and the most relevant entry points for understanding the research prototype.

The document is intended for readers who want to inspect the implementation behind the current NeuroDivSim research prototype. It is not a complete API manual or developer handbook. Its purpose is to make the main responsibilities, data flow and implementation boundaries visible.

The basic technical relationship can be summarized as follows:

```text
User interface
        │
        ▼
Frontend (Streamlit)
        │
        ▼
Backend (FastAPI)
        │
        ▼
Workflow (LangGraph)
        │
        ├──────────────► LLM-supported model construction
        │
        └──────────────► Deterministic simulation
```

## 2. Project structure

The repository is organized into backend, frontend, prompt templates and tests. The structure separates domain processing, user interface code and LLM-supported model construction.

```text
backend/          FastAPI backend, workflow, LLM integration and domain logic
frontend/         Streamlit frontend, workflow pages and result presentation
backend/prompts/  Prompt templates for scenario analysis, model generation and revision
tests/            Unit and integration tests
```

The domain-specific backend modules are located under `backend/domains/`. They include scenario analysis, model construction, planning, simulation, evaluation and cognitive reference configurations. Technical workflow orchestration is implemented in `backend/workflow/`, while feature-oriented frontend views are organized under `frontend/features/`.

## 3. Important entry points

### Backend

The backend entry point is `backend/main.py`. It creates the FastAPI application and registers the API routes. Domain-specific processing is delegated to routes, workflow nodes and domain modules.

The central API route is implemented in `backend/api/routes.py`. It exposes the workflow endpoint `/workflow/dispatch`, receives workflow commands from the frontend, updates the shared workflow state and returns structured responses to the frontend.

### Frontend

The frontend entry point is `frontend/app.py`. It initializes the Streamlit application, loads shared styles and renders the current workflow view.

The shared frontend state is managed in `frontend/state.py`. This file contains the default scenario, session initialization and helper functions that transfer backend workflow responses into the frontend state.

### Workflow

The state-based workflow is built in `backend/workflow/graph.py`. The file defines the LangGraph workflow, registers processing steps as nodes and specifies transitions between scenario analysis, model generation, revision, simulation and result preparation.

The shared workflow state is defined in `backend/workflow/state.py`. It acts as the data contract between workflow nodes and stores scenario data, generated models, simulation inputs, results and visualization data.

## 4. Backend organization

### API and transport

The API layer is located in `backend/api/` and `backend/transport/`. `backend/api/routes.py` provides the HTTP endpoints, while the schemas in `backend/transport/schemas/` define the structure of incoming and outgoing workflow messages.

This separation prevents the frontend from calling domain functions directly. Instead, communication takes place through structured HTTP messages and validated payloads.

### Workflow orchestration

`backend/workflow/` contains the technical orchestration of the analysis process. Individual processing steps are implemented in `backend/workflow/nodes/`, including nodes for scenario analysis, model construction, planning, simulation, revision and result preparation.

`backend/workflow/routing.py` defines the routing conditions that determine the next processing step. This makes it possible to rerun selected workflow sections, for example after human revision of generated models.

### LLM integration and prompt management

The LLM integration is implemented in `backend/core/llm/client.py`. This module configures the OpenAI-compatible chat client, structured output models and shared error handling for LLM calls.

Prompt texts are stored outside the production code in `backend/prompts/`. They are loaded through `backend/core/llm/prompt_loader.py`. This separation keeps prompt templates inspectable and avoids embedding long prompt texts directly in the application logic.

### Domain modules

The most relevant backend domains are:

```text
backend/domains/scenario/    Scenario and screenshot analysis
backend/domains/models/      Task, interface and environment models
backend/domains/planning/    Simulation plan and derived parameters
backend/domains/simulation/  Simulation engine, metrics, events and results
backend/domains/users/       Predefined cognitive reference configurations
backend/domains/evaluation/  Selection and description of evaluation metrics
```

The domain structure keeps model construction, planning, simulation and result preparation as separate responsibilities instead of concentrating all domain logic in a single service layer.

### Simulation

The central simulation logic is located in `backend/domains/simulation/`. The file `backend/domains/simulation/engine.py` executes the time-discrete simulation. Supporting calculations are organized in subdirectories such as `algorithms/`, `metrics/` and `events/`.

This structure reflects the central conceptual separation of the prototype. The LLM constructs structured simulation inputs, while the simulation itself is deterministic after the generated models have been inspected and confirmed.

## 5. Frontend organization

The frontend implements NeuroDivSim as a multi-step analysis workflow. View control is located in `frontend/workflow/`, where workflow steps, navigation and shared UI elements are defined.

Feature-specific views are located under `frontend/features/`:

```text
frontend/features/user_profiles/        Selection of cognitive reference configurations
frontend/features/evaluation_goals/     Selection of metrics for analysis
frontend/features/scenario/             Scenario input and optional screenshot support
frontend/features/task_flow/            Review of the generated interaction steps
frontend/features/dimensions/           Review of extracted scenario dimensions
frontend/features/models/               Review of simulation foundations
frontend/features/computed_parameters/  Simulation plan and derived values
frontend/features/simulation/           Simulation results
```

The result presentation in `frontend/features/simulation/` is further separated into components for summaries, charts, events and recommendations. CSS fragments are organized under `styles/`, while shared helper functions are located in `utils/`.

Backend communication is handled through `frontend/shared/services/workflow_api.py` and `frontend/shared/services/workflow_payloads.py`. This keeps the presentation layer separate from the concrete structure of HTTP payloads.

## 6. Typical program flow

A full run follows a fixed conceptual structure implemented through frontend actions, backend commands and workflow nodes.

The workflow is orchestrated by LangGraph. Data is passed between processing steps through the shared workflow state.

1. A usage scenario is described in the frontend. An interface screenshot can optionally be added.
2. The backend analyzes the scenario description and extracts structured signals for task, interface and environment.
3. Task Model, Interface Model and Environment Model are generated from these signals.
4. The generated models are shown in the frontend and can be inspected or revised.
5. A simulation plan is prepared from the model values and selected cognitive reference configurations.
6. Derived parameters are calculated deterministically from existing model values.
7. The simulation engine processes the interaction steps in discrete time and produces states, metrics, events and timeline data.
8. The frontend presents the results as reference configuration comparison, trajectories, event overview and design recommendations.

The flow therefore combines LLM-supported interpretation with deterministic downstream simulation. Model construction prepares structured simulation inputs; the subsequent simulation calculations and rule-based recommendations do not use the LLM.

## 7. Central implementation files

### `backend/api/routes.py`

This file is the main integration point between frontend and backend. It receives workflow commands, validates their payloads, invokes the LangGraph workflow and converts the resulting state into a structured response.

### `backend/workflow/graph.py`

This file defines the state-based workflow. It registers the nodes for scenario analysis, model generation, planning, simulation and result preparation. It is important for understanding how the prototype avoids a single monolithic processing function.

### `backend/workflow/state.py`

This file defines the shared workflow state. It shows which information is passed between frontend, model construction and simulation, including scenario data, generated models, selected metrics, simulation plans and results.

### `backend/core/llm/client.py`

This file centralizes LLM calls. It configures the chat client, connects prompt templates with structured output schemas and contains the functions used for scenario analysis, screenshot analysis and model generation.

### `backend/core/llm/prompt_loader.py`

This file defines how prompt templates are found and loaded from `backend/prompts/`. It is relevant because prompt texts remain inspectable as separate artifacts rather than being hidden inside Python functions.

### `backend/domains/planning/services/computed_parameters.py`

This file calculates derived parameters from existing task, interface and environment values. The calculations are deterministic and provide intermediate simulation inputs.

### `backend/domains/simulation/engine.py`

This file contains the time-discrete simulation engine. It processes the modeled interaction step by step and coordinates state updates, metric calculation, event evaluation, progress calculation and timeline creation.

### `backend/domains/simulation/recommendations.py`

This file contains the rule-based recommendation layer. It derives design recommendations from simulation results, relevant events, metrics and affected interaction steps.

### `backend/domains/users/services/user_profiles.py`

This file provides access to the predefined cognitive reference configurations. It makes visible that the configurations are fixed modeling assumptions, are not generated from the usage scenario and should not be interpreted as representations of individual people or population averages.

### `frontend/state.py`

This file manages shared frontend state. It stores the default scenario, backend state, selected cognitive reference configurations, model values and simulation results.

### `frontend/shared/services/workflow_api.py`

This file handles frontend calls to the backend workflow endpoint and centralizes handling of backend responses and errors.

### `frontend/features/simulation/view.py`

This file is the entry point for the result presentation in the frontend. It coordinates the display of reference configuration comparisons, trajectories, events and recommendations.

## 8. Extension points

The existing structure supports adding further cognitive reference configurations at the profile definition level under `backend/domains/users/`. Keeping these definitions centralized makes the available configurations explicit and allows them to be included consistently in the simulation plan.

Such additions would extend the set of modeling assumptions available for comparison. They would not by themselves provide empirical validation or representative models of diagnostic populations.

Additional simulation metrics can be added within the simulation metrics structure under `backend/domains/simulation/metrics/`. The registry mechanism supports their integration into simulation execution and later result presentation.

Additional events can be added under `backend/domains/simulation/events/` and registered through the existing event registry. This keeps threshold-based event logic separate from the central simulation loop.

Prompt templates can be revised under `backend/prompts/` without embedding long prompt texts into the production code. Schema changes, however, require coordinated updates to prompts, Pydantic models, workflow processing and frontend presentation.

Frontend result presentation is organized under `frontend/features/simulation/`. Changes to result display should preserve the separation between raw simulation output, result aggregation and visual presentation.
