"""Prompt resolver wiring for the support-triage project."""

from __future__ import annotations

from importlib.resources import files

from typeflux import InlineResolver, PromptRef, ResolvedPrompt
from typeflux.registry.langfuse import LangfuseResolver

from .config import Settings

_PROMPTS: dict[str, str] = {
    "classify.txt": "triage-classify",
    "route.txt": "triage-route",
    "draft.txt": "triage-draft",
    "package.txt": "triage-package",
}


def inline_resolver() -> InlineResolver:
    """Build an InlineResolver from packaged mustache prompt files."""
    prompt_dir = files("support_triage_project.prompts")
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


def langfuse_resolver(settings: Settings | None = None) -> LangfuseResolver:
    """Build a Langfuse-backed resolver from shared root `.env` settings."""
    runtime_settings = settings or Settings()
    return LangfuseResolver(
        host=runtime_settings.langfuse_host,
        public_key=runtime_settings.langfuse_public_key,
        secret_key=runtime_settings.langfuse_secret_key,
    )
