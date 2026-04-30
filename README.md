# Typeflux Tutorial Path

This repository walks through Typeflux in three passes. Each pass introduces one new idea and keeps the earlier ideas visible instead of hiding them behind a framework.

1. [Getting Started](getting_started/README.md)
   A notebook-first walkthrough. Everything is defined inline: schemas, prompts, a fake provider, and a tiny workflow.

2. [Simple Typeflux Project](simple_email_project/README.md)
   A small package with `prompts/`, `steps/`, and `workflows/`. It classifies an email intent and drafts a reply from a YAML workflow.

3. [Support Triage Project](support_triage_project/README.md)
   A fuller support workflow with YAML, deterministic hooks, an observer, domain config, and a script to bootstrap prompts into Langfuse.

## Shared Environment

Copy the root example env once:

```bash
cp .env.example .env
```

The same `.env` is used by every project:

- `OPENAI_API_KEY` and `OPENAI_MODEL` for the simple email project.
- `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` for the support triage project.
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`, and `LANGFUSE_PROMPT_LABEL` for prompt bootstrap and Langfuse-backed prompt resolution.

## Install

The demos are intentionally independent. Install the project you are reading from its folder:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e "getting_started[dev]"
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e "simple_email_project[dev]"
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -e "support_triage_project[dev,langfuse]"
```

Run all tests from the repo root after installing both packages:

```bash
python -m pytest simple_email_project support_triage_project
```
