# NeuroDivSim

NeuroDivSim is an interactive research prototype for model-based reflection on cognitive diversity in interface design. It supports designers and developers during early design and prototyping by turning usage scenarios into inspectable models and by comparing the same modeled situation across explicit cognitive reference configurations.

The prototype explores simulation as a tool for reflection, not prediction. It does not use a Large Language Model as a synthetic user or as a surrogate for a human participant. Instead, generative AI supports the construction of structured task, interface and environment models from natural-language input and, optionally, an interface screenshot. After human review, downstream processing is deterministic.

NeuroDivSim should not be interpreted as predicting neurodivergent behavior, representing population averages or replacing participatory design, accessibility evaluation, usability testing or empirical research with neurodivergent people. Its outputs describe consequences of explicit modeling assumptions for a specific design situation and are intended to support design reflection before or between opportunities for empirical evaluation.

## Overview

NeuroDivSim addresses a design-stage problem: knowledge about cognitive diversity often needs to be translated into concrete interface, task and context decisions while a design is still open to revision. The system adds a structured reflection step to this process. It keeps the modeled usage situation constant while varying selected cognitive assumptions, making it possible to inspect how these assumptions affect simulated states, metrics, events and design recommendations.

This framing is complementary to approaches that use generative agents, personas or synthetic users to produce user-like behavior or feedback. NeuroDivSim does not ask an LLM to act as a neurodivergent person. The LLM is used only to help formalize the usage situation into inspectable model inputs. The simulation then examines the modeled consequences of confirmed inputs and fixed reference configurations.

## How It Works

A typical workflow consists of the following steps:

1. A designer describes a usage scenario in natural language and can optionally provide an interface screenshot.
2. The backend uses an LLM to support construction of structured representations of the usage situation.
3. These representations include a task model, an interface model and an environment model.
4. The generated models are shown in the frontend and can be inspected or revised before simulation.
5. Cognitive assumptions are represented separately through cognitive reference configurations.
6. The reviewed scenario models are combined with the selected configurations.
7. Subsequent simulation processing is deterministic.
8. The simulation produces states, metrics and events for the modeled interaction.
9. Results can be compared across cognitive reference configurations.
10. Rule-based design recommendations connect modeled conditions to potentially demanding interaction steps.

Given identical confirmed task, interface, environment and cognitive configuration inputs, the downstream simulation produces identical state trajectories, metrics and events. This reproducibility claim applies only to the deterministic simulation stage after LLM-supported model construction and human review.

## Cognitive Reference Configurations

NeuroDivSim currently includes a Generic comparison configuration, an ADHD-informed reference configuration and a Dyslexia-informed reference configuration. These configurations are modeling constructs. They abstract selected interaction-relevant cognitive characteristics so that different assumptions can be compared within the same modeled usage situation.

The configurations do not represent individual neurodivergent people, representative members of diagnostic populations or empirically estimated population averages. Their numerical values, weights and thresholds are heuristic operationalizations informed by literature and design rationale. Inspectability makes these assumptions visible and revisable; it does not make them empirically valid.

## System Architecture

NeuroDivSim separates presentation, workflow orchestration, LLM-supported model construction and deterministic simulation.

```text
Frontend (Streamlit)
        │
        ▼
Backend API (FastAPI)
        │
        ▼
Workflow orchestration (LangGraph)
        │
        ├──────────────► LLM-supported scenario and model construction
        │
        └──────────────► Deterministic planning, simulation and results
```

The frontend provides the multi-step user interface. The backend exposes the workflow endpoint `/workflow/dispatch`, coordinates processing through LangGraph and keeps the LLM integration encapsulated in the backend. Prompt templates are stored separately under `backend/prompts/`. The simulation engine processes the confirmed model inputs and cognitive reference configurations in discrete time steps.

## Installation

### Requirements

- Python 3.12
- An OpenAI API key or an OpenAI-compatible local LLM endpoint

Python dependencies are listed in `requirements.txt`.

Clone the repository and change into the project directory:

```bash
git clone https://github.com/eskebfd/neurodivsim.git
cd neurodivsim
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a local configuration file:

```bash
cp .env.example .env
```

Real API keys must never be committed to the repository.

## Configuration

For the default OpenAI setup, set an API key in `.env`:

```text
OPENAI_API_KEY=<your-api-key>
```

Additional optional variables are documented in `.env.example`.

### LLM configuration

The LLM integration is implemented in the backend through an OpenAI-compatible chat client in `backend/core/llm/client.py`. Without additional configuration, NeuroDivSim uses the model `gpt-4o-mini` and the value from `OPENAI_API_KEY`.

The model name, base URL and API key can optionally be configured through neutral environment variables:

```text
LLM_MODEL=<model-name>
LLM_BASE_URL=<openai-compatible-base-url>
LLM_API_KEY=<api-key>
```

If `LLM_API_KEY` is not set, `OPENAI_API_KEY` is used.

A locally provided Ollama model can be used if it is exposed through an OpenAI-compatible endpoint and reliably supports the structured outputs required by the application. Ollama must be running locally and the selected model must already be available.

Example:

```text
LLM_MODEL=llama3.1
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
```

## Running NeuroDivSim

Run the following commands from the project directory.

Start the backend:

```bash
python -m uvicorn backend.main:app --reload
```

Start the frontend in a second terminal:

```bash
python -m streamlit run frontend/app.py
```

The frontend calls the backend API at `http://127.0.0.1:8000`. The central workflow endpoint is `/workflow/dispatch`. If the backend runs on a different local port, set `NEURODIVSIM_BACKEND_URL` in `.env` before starting Streamlit.

## Running Tests

Run the test suite with:

```bash
pytest -q
```

For local test runs without a real API key, a dummy value can be used:

```bash
OPENAI_API_KEY=test pytest -q
```

The tests are structured so that no real external LLM calls are executed.

## Repository Structure

```text
backend/      FastAPI backend, workflow, LLM integration, domain logic and simulation
frontend/     Streamlit frontend and UI components
tests/        Unit and integration tests
```

Important backend areas:

```text
backend/api/          API routes
backend/core/         LLM client, prompt loading and logging
backend/domains/      Domain modules for models, planning, simulation, cognitive configurations and evaluation
backend/prompts/      Prompt templates
backend/transport/    Request and response schemas
backend/workflow/     LangGraph workflow and shared workflow state
```

## Limitations

NeuroDivSim is a research prototype for design reflection. The current simulation relationships, cognitive reference configurations, parameter values and recommendation rules have not been empirically calibrated as behavioral models. Simulation outputs should therefore be read as consequences of explicit model assumptions under a fixed usage context, not as claims about actual users.

The prototype does not reproduce lived experience, diagnose accessibility barriers or determine which design decision should be adopted. Its results can help identify questions for closer design consideration and later empirical evaluation.


## License

No license file is currently included in this repository.
