"""Prompt resolver wiring for the support-triage demo."""

from __future__ import annotations

from importlib.resources import files

from typeflux import InlineResolver, PromptRef, ResolvedPrompt, StepSpec

from .workflow.steps import classify_ticket, draft_response, package_for_review, route_ticket

_PROMPTS: dict[str, StepSpec] = {
    "classify.txt": classify_ticket,
    "route.txt": route_ticket,
    "draft.txt": draft_response,
    "package.txt": package_for_review,
}


def inline_resolver() -> InlineResolver:
    """Build an InlineResolver from the packaged mustache prompt files."""
    prompt_dir = files("support_triage.prompts")
    prompts: dict[tuple[str, str], ResolvedPrompt] = {}
    for filename, step in _PROMPTS.items():
        text = prompt_dir.joinpath(filename).read_text(encoding="utf-8")
        ref = PromptRef(step.prompt_ref.name)
        prompts[(ref.name, ref.version)] = ResolvedPrompt.from_text(
            ref,
            text,
            template_format="mustache",
        )
    return InlineResolver(prompts=prompts)

