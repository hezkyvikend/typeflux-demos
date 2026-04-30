"""Sample email input for the simple Typeflux project."""

from __future__ import annotations

from ..schemas import EmailInput


def sample_email() -> EmailInput:
    """Return a representative inbound customer email."""
    return EmailInput(
        sender="riley@example.com",
        subject="Question about upgrading seats",
        body=(
            "Hi team, we are adding five people next month and want to know "
            "whether the Pro plan supports consolidated billing. Can someone "
            "point me in the right direction?"
        ),
    )
