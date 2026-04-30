"""CLI entry point and runtime assembly for the simple email project."""

from __future__ import annotations

import argparse
import logging
import sys

from typeflux.providers.base import ModelProvider
from typeflux.providers.openai import OpenAIProvider
from typeflux.registry.base import PromptResolver

from .config import Settings
from .demo import sample_email
from .registry import inline_resolver
from .schemas import DraftReply, EmailInput
from .workflows.pipeline import run


def _configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(levelname)s %(name)s: %(message)s",
    )


def run_email(
    email: EmailInput,
    *,
    provider: ModelProvider | None = None,
    resolver: PromptResolver | None = None,
    settings: Settings | None = None,
) -> DraftReply:
    """Execute the workflow for a single inbound email."""
    runtime_settings = settings or Settings()
    if provider is None:
        provider = OpenAIProvider(
            api_key=runtime_settings.openai_api_key,
            default_model=runtime_settings.openai_model,
        )

    return run(
        email,
        provider=provider,
        resolver=resolver or inline_resolver(),
    )


def run_sample_email(
    *,
    provider: ModelProvider | None = None,
    resolver: PromptResolver | None = None,
    settings: Settings | None = None,
) -> DraftReply:
    """Execute the workflow for the packaged sample email."""
    return run_email(
        sample_email(),
        provider=provider,
        resolver=resolver,
        settings=settings,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Typeflux email-intent demo using YAML, local prompts, and OpenAI."
    )
    parser.parse_args(argv)

    settings = Settings()
    _configure_logging(settings)

    reply = run_sample_email(settings=settings)
    print(reply.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
