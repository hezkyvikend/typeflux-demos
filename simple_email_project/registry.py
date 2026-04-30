"""Prompt resolver wiring for the simple email project."""

from __future__ import annotations

from importlib.resources import files

from typeflux import InlineResolver, PromptRef, ResolvedPrompt

_PROMPTS: dict[str, str] = {
    "classify_intent.txt": "email-classify-intent",
    "draft_reply.txt": "email-draft-reply",
}


def inline_resolver() -> InlineResolver:
    """Build an InlineResolver from packaged mustache prompt files."""
    prompt_dir = files("simple_email_project.prompts")
    prompts: dict[tuple[str, str], ResolvedPrompt] = {}
    for filename, prompt_name in _PROMPTS.items():
        text = prompt_dir.joinpath(filename).read_text(encoding="utf-8")
        ref = PromptRef(prompt_name)
        prompts[(ref.name, ref.version)] = ResolvedPrompt.from_text(
            ref,
            text,
            template_format="mustache",
        )
    return InlineResolver(prompts=prompts)
