"""CLI entry point and runtime assembly for the support-triage demo."""

from __future__ import annotations

import argparse
import logging
import sys

from typeflux.providers.anthropic import AnthropicProvider
from typeflux.providers.base import ModelProvider
from typeflux.registry.base import PromptResolver

from .config import Settings
from .demo import sample_ticket
from .registry import inline_resolver
from .schemas import ReviewPacket, TicketInput
from .workflow.pipeline import run


def _configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(levelname)s %(name)s: %(message)s",
    )


def run_ticket(
    ticket: TicketInput,
    *,
    provider: ModelProvider | None = None,
    resolver: PromptResolver | None = None,
    settings: Settings | None = None,
) -> ReviewPacket:
    """Execute the workflow for a single support ticket."""
    runtime_settings = settings
    if provider is None:
        runtime_settings = runtime_settings or Settings()
        provider = AnthropicProvider(
            api_key=runtime_settings.anthropic_api_key,
            default_model=runtime_settings.anthropic_model,
        )

    return run(
        ticket,
        provider=provider,
        resolver=resolver or inline_resolver(),
    )


def run_sample_ticket(
    *,
    provider: ModelProvider | None = None,
    resolver: PromptResolver | None = None,
    settings: Settings | None = None,
) -> ReviewPacket:
    """Execute the workflow for the packaged sample support ticket."""
    return run_ticket(
        sample_ticket(),
        provider=provider,
        resolver=resolver,
        settings=settings,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Typeflux support-triage demo using local prompt files and Anthropic."
    )
    parser.parse_args(argv)

    settings = Settings()
    _configure_logging(settings)

    packet = run_sample_ticket(settings=settings)
    print(packet.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
