# Simple Typeflux Project

This project is the first structured example after the notebook. It shows how a small Typeflux app is usually organized once inline code becomes too cramped.

## What It Teaches

- `prompts/` keeps prompt text in files.
- `steps/` holds Python step hooks for deterministic post-processing.
- `workflows/` contains a YAML workflow definition and a tiny loader.
- `schemas/` defines the typed contracts between steps.
- `registry.py` converts local prompt files into an `InlineResolver`.

The workflow classifies an inbound email, then drafts a reply.

## Step Definition Styles

This project intentionally uses two step styles in the same workflow.

### Pure YAML Step

`classify_intent` is defined entirely in [workflows/email_reply.yaml](workflows/email_reply.yaml):

```yaml
- name: classify_intent
  input_type: EmailInput
  output_type: IntentClassification
  prompt_ref: email-classify-intent
  retries: 2
```

This is the simplest form. Typeflux loads the input and output schemas, fetches the prompt by `prompt_ref`, calls the provider, and validates the model output. There is no Python hook because the LLM output is already the whole step result.

### Decorator And Hook Step

`draft_reply` is registered in [steps/email_steps.py](steps/email_steps.py):

```python
@step(prompt=PromptRef("email-draft-reply"))
def draft_reply(input: IntentClassification, output: DraftReply) -> DraftReply:
    ...
```

The decorator turns the function into a reusable `StepSpec`. Typeflux still asks the LLM for a `DraftReply`, but then it calls the Python hook with both the previous step input and the validated LLM output. The hook copies deterministic fields like `to`, `subject`, and `intent` so those are not left to the model.

### How They Compose

The YAML composes both styles:

```yaml
steps:
  - name: classify_intent
    ...

  - step: draft_reply
```

The first entry creates an inline step directly from YAML. The second entry references a decorated step from `step_module: simple_email_project.steps`. Typeflux validates that `classify_intent` outputs `IntentClassification`, which is exactly what `draft_reply` expects as input, so the chain is type-checked at load time.

### Why The Runner Uses `cast`

`run_workflow(...)` can run any workflow, so its static return type is the broad `BaseModel`. This workflow's YAML guarantees the final step returns `DraftReply`, and Typeflux validates that at runtime. The `cast(DraftReply, result)` in [workflows/pipeline.py](workflows/pipeline.py) tells the type checker what the YAML already guarantees, without changing runtime behavior.

## Layout

```text
simple_email_project/
├── prompts/      # local mustache prompt files
├── steps/        # hook-backed Typeflux steps
├── workflows/    # YAML workflow + runner
├── schemas/      # pydantic contracts
├── demo/         # sample input
├── tests/        # deterministic tests with a fake provider
├── registry.py   # local prompt resolver
└── main.py       # CLI entry point
```

## Setup

From the repo root:

```bash
cp .env.example .env
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e "simple_email_project[dev]"
```

For live runs, fill in:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Run

```bash
python -m simple_email_project.main
```

or after install:

```bash
simple-email
```

## Test

```bash
python -m pytest simple_email_project
```
