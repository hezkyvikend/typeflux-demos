"""Pipeline step specs for the support-triage demo."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from functools import lru_cache

from typeflux import PromptRef, step

from ..domain import COMPLIANCE_FOOTER, DomainConfig, is_within_business_hours, load_config, redact_pii
from ..schemas import (
    Classification,
    DraftReply,
    ReviewPacket,
    RoutingDecision,
    Urgency,
)


def _default_clock() -> datetime:
    return datetime.now(UTC)


_CLOCK: Callable[[], datetime] = _default_clock


@lru_cache(maxsize=1)
def _config() -> DomainConfig:
    return load_config()


@step(prompt=PromptRef("triage-route"))
def route_ticket(input: Classification, output: RoutingDecision) -> RoutingDecision:
    """Validate the team and override to on-call after hours when urgent."""
    cfg = _config()
    if output.team not in cfg.teams:
        raise ValueError(
            f"route_ticket: LLM returned unknown team {output.team!r}; "
            f"known teams: {sorted(cfg.teams)}"
        )

    after_hours = not is_within_business_hours(_CLOCK(), cfg)
    urgent = input.urgency in (Urgency.HIGH, Urgency.CRITICAL)
    if after_hours and urgent:
        return output.model_copy(
            update={
                "team": "oncall-engineer",
                "on_call_engineer": cfg.on_call_primary,
                "escalated": True,
                "sla_hours": 1 if input.urgency is Urgency.CRITICAL else 4,
            }
        )

    return output


@step(prompt=PromptRef("triage-draft"))
def draft_response(input: RoutingDecision, output: DraftReply) -> DraftReply:
    """Redact accidental PII and append the compliance footer."""
    redacted_body, count = redact_pii(output.body)
    return output.model_copy(
        update={
            "body": redacted_body + COMPLIANCE_FOOTER,
            "redaction_count": count,
            "escalated": input.escalated,
        }
    )


@step(prompt=PromptRef("triage-package"))
def package_for_review(input: DraftReply, output: ReviewPacket) -> ReviewPacket:
    """Require approval when PII was redacted or the ticket was escalated."""
    approval_required = input.redaction_count > 0 or input.escalated
    return output.model_copy(update={"approval_required": approval_required})
