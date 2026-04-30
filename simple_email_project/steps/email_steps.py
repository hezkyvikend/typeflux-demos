"""Hook-backed steps for the simple email workflow."""

from __future__ import annotations

from typeflux import PromptRef, step

from ..schemas import DraftReply, IntentClassification


@step(prompt=PromptRef("email-draft-reply"))
def draft_reply(input: IntentClassification, output: DraftReply) -> DraftReply:
    """Copy deterministic fields that should not be left to the model."""
    subject = output.subject
    if not subject.lower().startswith("re:"):
        subject = f"Re: {input.subject}"

    return output.model_copy(
        update={
            "to": input.sender,
            "subject": subject,
            "intent": input.intent,
        }
    )
