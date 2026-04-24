# Support Triage YAML

This folder is a self-contained Typeflux demo project.

It uses:

- local prompt files under `prompts/`
- a declarative workflow definition under `workflow/support_triage_yaml.yaml`
- `InlineResolver` for prompt loading
- `typeflux.load_from_yaml(...)` to compile the workflow
- `AnthropicProvider` for the live model call

## Layout

```text
support_triage_yaml/
├── config/      # structured environment-backed settings
├── demo/        # sample ticket data for the CLI/demo path
├── domain/      # deterministic business rules + domain config
├── prompts/     # prompt source of truth
├── schemas/     # pydantic workflow contracts
├── tests/       # unit/integration tests for core seams
├── workflow/    # yaml workflow definition + pipeline wiring
├── registry.py  # prompt resolver wiring
└── main.py      # CLI entry point + runtime assembly
```

## Setup

From inside this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e .
```

For local test tooling:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e .[dev]
```

## Run

```bash
cp .env.example .env
# fill in ANTHROPIC_API_KEY first
python -m support_triage_yaml.main
```

You can also use the console script after install:

```bash
support-triage-yaml
```

## Test

```bash
pytest
```
