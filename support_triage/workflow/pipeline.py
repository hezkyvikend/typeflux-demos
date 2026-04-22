"""The support-triage workflow."""

from __future__ import annotations

from typing import cast

from typeflux import InlineResolver, WorkflowSpec, run_workflow
from typeflux.observability.observer import NoOpObserver, Observer
from typeflux.providers.base import ModelProvider
from typeflux.registry.base import PromptResolver

from ..schemas import ReviewPacket, TicketInput
from .steps import classify_ticket, draft_response, package_for_review, route_ticket

SupportTriagePipeline = WorkflowSpec(
    name="SupportTriageInlineAnthropicPipeline",
    steps=(
        classify_ticket,
        route_ticket,
        draft_response,
        package_for_review,
    ),
)


def run(
    ticket: TicketInput,
    *,
    provider: ModelProvider,
    resolver: PromptResolver | None = None,
    observer: Observer | None = None,
) -> ReviewPacket:
    """Execute the support-triage workflow end to end."""
    result = run_workflow(
        SupportTriagePipeline,
        ticket,
        resolver=resolver or InlineResolver(),
        provider=provider,
        observer=observer or NoOpObserver(),
    )
    return cast(ReviewPacket, result)

