from __future__ import annotations

from pydantic import BaseModel

from simple_email_project.demo import sample_email
from simple_email_project.main import run_sample_email
from simple_email_project.schemas import DraftReply, EmailIntent, IntentClassification
from simple_email_project.workflows.pipeline import EmailReplyWorkflow
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
        if output_schema is IntentClassification:
            email = sample_email()
            return IntentClassification(
                subject=email.subject,
                body=email.body,
                sender=email.sender,
                intent=EmailIntent.SALES,
                urgency="normal",
                reason="The sender asks about adding seats and plan details.",
            )
        if output_schema is DraftReply:
            return DraftReply(
                to="placeholder@example.com",
                subject="Question about upgrading seats",
                body="Thanks for reaching out. Our team can help with seat upgrades and billing options.",
                intent=EmailIntent.OTHER,
            )
        raise AssertionError(f"Unexpected schema: {output_schema}")


def _resolver() -> InlineResolver:
    prompts = {}
    for name in ["email-classify-intent", "email-draft-reply"]:
        ref = PromptRef(name)
        prompts[(ref.name, ref.version)] = ResolvedPrompt.from_text(
            ref,
            "placeholder {{subject}}",
            template_format="mustache",
        )
    return InlineResolver(prompts=prompts)


def test_app_runs_sample_email_end_to_end() -> None:
    reply = run_sample_email(provider=_StubProvider(), resolver=_resolver())

    assert isinstance(reply, DraftReply)
    assert reply.to == "riley@example.com"
    assert reply.subject == "Re: Question about upgrading seats"
    assert reply.intent is EmailIntent.SALES


def test_pipeline_uses_yaml_step_order() -> None:
    assert [step.name for step in EmailReplyWorkflow.steps] == [
        "classify_intent",
        "draft_reply",
    ]
    assert EmailReplyWorkflow.steps[0].has_hook is False
    assert EmailReplyWorkflow.steps[1].has_hook is True
