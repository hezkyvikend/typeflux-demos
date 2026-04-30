"""Simple email-intent Typeflux project."""

from .schemas import DraftReply, EmailInput, EmailIntent, IntentClassification
from .workflows.pipeline import EmailReplyWorkflow

__all__ = [
    "DraftReply",
    "EmailInput",
    "EmailIntent",
    "EmailReplyWorkflow",
    "IntentClassification",
]
