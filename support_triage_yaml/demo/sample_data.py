"""Representative sample inputs for the support-triage demo."""

from __future__ import annotations

from datetime import UTC, datetime

from ..schemas import TicketInput


def sample_ticket() -> TicketInput:
    """Return a representative sample support ticket for the CLI demo."""
    return TicketInput(
        customer_id="cust-1042",
        subject="Charged twice for the same invoice",
        body=(
            "Hi - your system billed me twice this month for the same invoice "
            "and I'm getting worried this will affect my credit card. "
            "Can someone look into this urgently?\n\n"
            "You can reach me at jane.doe@example.com or on 555-123-4567."
        ),
        received_at=datetime.now(UTC),
    )

