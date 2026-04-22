from __future__ import annotations

from pydantic import BaseModel

from support_triage.demo import sample_ticket
from support_triage.main import run_sample_ticket
from support_triage.schemas import (
    Classification,
    DraftReply,
    ReviewPacket,
    RoutingDecision,
    Urgency,
)
from support_triage.workflow.pipeline import SupportTriagePipeline
from typeflux import ChatMessage, InlineResolver, PromptRef, ResolvedPrompt


class _StubProvider:
    def structured_call(
        self,
        *,
        messages: list[ChatMessage],
        output_schema: type[BaseModel],
        model: str | None = None,
        temperature: float | None = None,
    ) -> BaseModel:
        del messages, model, temperature
        if output_schema is Classification:
            return Classification(
                category="billing",
                urgency=Urgency.HIGH,
                sentiment=-0.7,
                topics=["invoice", "billing"],
            )
        if output_schema is RoutingDecision:
            return RoutingDecision(
                team="billing",
                sla_hours=4,
                on_call_engineer=None,
                escalated=False,
            )
        if output_schema is DraftReply:
            return DraftReply(
                subject="Re: Invoice question",
                body="Please reply to jane.doe@example.com or call 555-123-4567.",
                tone="apologetic",
            )
        if output_schema is ReviewPacket:
            return ReviewPacket(
                verdict="flag",
                summary="Customer asks about duplicate billing and receives a drafted response.",
                approval_required=False,
            )
        raise AssertionError(f"Unexpected schema: {output_schema}")


def _resolver() -> InlineResolver:
    refs = [
        "triage-classify",
        "triage-route",
        "triage-draft",
        "triage-package",
    ]
    prompts = {
        (name, "production"): ResolvedPrompt.from_text(
            PromptRef(name),
            "placeholder {{subject}}",
            template_format="mustache",
        )
        for name in refs
    }
    prompts[("triage-route", "production")] = ResolvedPrompt.from_text(
        PromptRef("triage-route"),
        "placeholder {{category}}",
        template_format="mustache",
    )
    prompts[("triage-draft", "production")] = ResolvedPrompt.from_text(
        PromptRef("triage-draft"),
        "placeholder {{team}}",
        template_format="mustache",
    )
    prompts[("triage-package", "production")] = ResolvedPrompt.from_text(
        PromptRef("triage-package"),
        "placeholder {{subject}}",
        template_format="mustache",
    )
    return InlineResolver(prompts=prompts)


def test_app_runs_sample_ticket_end_to_end() -> None:
    packet = run_sample_ticket(provider=_StubProvider(), resolver=_resolver())

    assert isinstance(packet, ReviewPacket)
    assert packet.approval_required is True


def test_pipeline_still_has_expected_step_order() -> None:
    assert [step.name for step in SupportTriagePipeline.steps] == [
        "classify_ticket",
        "route_ticket",
        "draft_response",
        "package_for_review",
    ]


def test_sample_ticket_returns_expected_input_type() -> None:
    ticket = sample_ticket()
    assert ticket.subject
