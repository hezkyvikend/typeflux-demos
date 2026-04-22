"""Pipeline step specs for the support-triage demo."""

from __future__ import annotations

import logging
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
    TicketInput,
    Urgency,
)

log = logging.getLogger("typeflux.triage")


def _default_clock() -> datetime:
    return datetime.now(UTC)


_CLOCK: Callable[[], datetime] = _default_clock


@lru_cache(maxsize=1)
def _config() -> DomainConfig:
    return load_config()


_CRITICAL_KEYWORDS = frozenset({"outage", "down", "broken", "cannot access", "can't access"})


@step(prompt=PromptRef("triage-classify"), retries=2)
def classify_ticket(input: TicketInput, output: Classification) -> Classification:
    """Clamp unjustified ``critical`` urgency to ``high``."""
    if output.urgency is not Urgency.CRITICAL:
        return output

    text = f"{input.subject}\n{input.body}".lower()
    has_keyword = any(keyword in text for keyword in _CRITICAL_KEYWORDS)
    very_negative = output.sentiment < -0.3
    if has_keyword or very_negative:
        return output

    log.info(
        "classify_ticket: clamping urgency critical->high for %s (sentiment=%.2f)",
        input.customer_id,
        output.sentiment,
    )
    return output.model_copy(update={"urgency": Urgency.HIGH})


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

