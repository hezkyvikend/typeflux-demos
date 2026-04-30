"""CLI entry point and runtime assembly for the support-triage project."""

from __future__ import annotations

import argparse
import logging
import sys

from typeflux.observability.observer import Observer
from typeflux.providers.anthropic import AnthropicProvider
from typeflux.providers.base import ModelProvider
from typeflux.registry.base import PromptResolver

from .config import Settings
from .demo import sample_ticket
from .observers import observer_from_alias
from .registry import inline_resolver, langfuse_resolver
from .schemas import ReviewPacket, TicketInput
from .workflows.pipeline import SupportTriageWorkflow, run


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
    observer: Observer | None = None,
    settings: Settings | None = None,
) -> ReviewPacket:
    """Execute the workflow for a single support ticket."""
    runtime_settings = settings or Settings()
    if provider is None:
        provider = AnthropicProvider(
            api_key=runtime_settings.anthropic_api_key,
            default_model=runtime_settings.anthropic_model,
        )

    return run(
        ticket,
        provider=provider,
        resolver=resolver or inline_resolver(),
        observer=observer,
    )


def run_sample_ticket(
    *,
    provider: ModelProvider | None = None,
    resolver: PromptResolver | None = None,
    observer: Observer | None = None,
    settings: Settings | None = None,
) -> ReviewPacket:
    """Execute the workflow for the packaged sample support ticket."""
    return run_ticket(
        sample_ticket(),
        provider=provider,
        resolver=resolver,
        observer=observer,
        settings=settings,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Typeflux support-triage demo using YAML, observers, and Anthropic."
    )
    parser.add_argument(
        "--registry",
        choices=["workflow", "inline", "langfuse"],
        default="workflow",
        help="Prompt registry to use at runtime. 'workflow' uses the YAML registry alias.",
    )
    parser.add_argument(
        "--observer",
        choices=["workflow", "logging", "langfuse", "none"],
        default="workflow",
        help="Observer to use at runtime. 'workflow' uses the YAML observer alias.",
    )
    args = parser.parse_args(argv)

    settings = Settings()
    _configure_logging(settings)

    registry_alias = SupportTriageWorkflow.registry if args.registry == "workflow" else args.registry
    resolver = langfuse_resolver(settings) if registry_alias == "langfuse" else inline_resolver()
    observer_alias = SupportTriageWorkflow.observer if args.observer == "workflow" else args.observer
    observer = observer_from_alias(observer_alias, settings)
    packet = run_sample_ticket(settings=settings, resolver=resolver, observer=observer)
    flush = getattr(observer, "flush", None)
    if callable(flush):
        flush()
    print(packet.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
