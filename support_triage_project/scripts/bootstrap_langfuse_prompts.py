"""Bootstrap support-triage prompts into Langfuse.

Run from the repo root after filling in `.env`:

    python support_triage_project/scripts/bootstrap_langfuse_prompts.py
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from support_triage_project.config import Settings
from support_triage_project.registry import _PROMPTS, langfuse_resolver
from support_triage_project.workflows.pipeline import SupportTriageWorkflow


def bootstrap_prompts() -> None:
    """Create a new Langfuse prompt version for each workflow prompt."""
    settings = Settings()
    resolver = langfuse_resolver(settings)
    prompt_dir = files("support_triage_project.prompts")
    steps_by_prompt = {step.prompt_ref.name: step for step in SupportTriageWorkflow.steps}

    for filename, prompt_name in _PROMPTS.items():
        step = steps_by_prompt[prompt_name]
        text = prompt_dir.joinpath(filename).read_text(encoding="utf-8")
        resolver.update_prompt(
            step,
            workflow_name=SupportTriageWorkflow.name,
            text=text,
            template_format="mustache",
            label=settings.langfuse_prompt_label,
            provider_name="anthropic",
            provider_model=settings.anthropic_model,
            temperature=0.0,
            tags=["typeflux", "support-triage"],
            commit_message="Bootstrap Typeflux tutorial prompt",
        )
        print(f"Bootstrapped {prompt_name}@{settings.langfuse_prompt_label}")


if __name__ == "__main__":
    bootstrap_prompts()
