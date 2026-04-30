# Support Triage Project

This is the most complete tutorial project. It keeps the same Typeflux ideas from the notebook and simple email project, then adds production-shaped concerns:

- YAML workflow definition
- local prompts that can also be bootstrapped into Langfuse
- deterministic Python hooks for routing, redaction, and approval rules
- `observer: langfuse` declared directly in the workflow YAML
- shared root `.env` settings

## Layout

```text
support_triage_project/
├── config/       # root .env-backed settings
├── demo/         # sample support ticket
├── domain/       # deterministic business rules + YAML config
├── observers/    # Typeflux observer implementations
├── prompts/      # local prompt source of truth
├── schemas/      # pydantic workflow contracts
├── scripts/      # Langfuse prompt bootstrap
├── steps/        # hook-backed Typeflux steps
├── tests/        # deterministic tests
├── workflows/    # YAML workflow + runner
├── registry.py   # inline and Langfuse resolvers
└── main.py       # CLI entry point
```

## Langfuse Walkthrough

The point of this project is to show both Langfuse prompt registry resolution and Langfuse tracing working from declarative Typeflux wiring. The workflow says:

```yaml
provider: anthropic
registry: langfuse
observer: langfuse
```

The CLI uses those workflow aliases by default, so after bootstrapping prompts the run command does not need any Langfuse-specific flags.

### Step 1: Set Environment

From the repo root:

```bash
cp .env.example .env
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e "support_triage_project[dev,langfuse]"
```

Fill in:

```text
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-5
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROMPT_LABEL=production
```

### Step 2: Bootstrap Prompts

This publishes each local prompt file into Langfuse with Typeflux metadata attached:

```bash
python support_triage_project/scripts/bootstrap_langfuse_prompts.py
```

### Step 3: Run With Langfuse Registry And Observer

Now run the workflow. Prompt resolution comes from `registry: langfuse`, and tracing comes from `observer: langfuse`:

```bash
support-triage
```

The satisfying bit: the code path does not change. Typeflux resolves prompt text from Langfuse, executes the YAML workflow, emits step events to the Langfuse observer, and flushes the trace before the command exits.

### Step 4: Check Langfuse

Open Langfuse and look at the latest trace. You should see the workflow span, each Typeflux step, generation details, hook spans for deterministic Python logic, inputs and outputs, and Typeflux metadata on the observations.

## Local Runs Without Langfuse

For a local run with packaged prompts and console step logs:

```bash
support-triage --registry inline --observer logging
```

For no observer at all:

```bash
support-triage --registry inline --observer none
```

## Test

```bash
python -m pytest support_triage_project
```
