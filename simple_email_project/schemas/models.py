"""Schemas for the simple email workflow."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EmailIntent(StrEnum):
    SALES = "sales"
    SUPPORT = "support"
    BILLING = "billing"
    FEEDBACK = "feedback"
    OTHER = "other"


Urgency = Literal["low", "normal", "high"]


class EmailInput(BaseModel):
    subject: str = Field(description="Email subject line.")
    body: str = Field(description="Full email body.")
    sender: str = Field(description="Sender email address.")


class IntentClassification(BaseModel):
    subject: str = Field(description="Original subject, copied forward for later steps.")
    body: str = Field(description="Original body, copied forward for later steps.")
    sender: str = Field(description="Original sender, copied forward for later steps.")
    intent: EmailIntent = Field(description="Primary intent of the email.")
    urgency: Urgency = Field(description="Response urgency.")
    reason: str = Field(description="One sentence explanation of the classification.")

    @field_validator("reason")
    @classmethod
    def _strip_reason(cls, value: str) -> str:
        return value.strip()


class DraftReply(BaseModel):
    to: str = Field(description="Recipient email address.")
    subject: str = Field(description="Reply subject line.")
    body: str = Field(description="Plain text reply body.")
    intent: EmailIntent = Field(description="Intent copied from classification for downstream systems.")
