"""Application boundary for the support-triage demo."""

from __future__ import annotations

from dataclasses import dataclass

from typeflux.providers.anthropic import AnthropicProvider
from typeflux.providers.base import ModelProvider
from typeflux.registry.base import PromptResolver

from .config import Settings
from .demo import sample_ticket
from .registry import inline_resolver
from .schemas import ReviewPacket, TicketInput
from .workflow.pipeline import run


@dataclass
class SupportTriageApp:
    """High-level application wrapper around the workflow."""

    provider: ModelProvider
    resolver: PromptResolver

    @classmethod
    def from_settings(cls, settings: Settings) -> SupportTriageApp:
        """Build the app with production-style runtime dependencies."""
        return cls(
            provider=AnthropicProvider(
                api_key=settings.anthropic_api_key,
                default_model=settings.anthropic_model,
            ),
            resolver=inline_resolver(),
        )

    def run_ticket(self, ticket: TicketInput) -> ReviewPacket:
        """Execute the workflow for a single support ticket."""
        return run(
            ticket,
            provider=self.provider,
            resolver=self.resolver,
        )

    def run_sample_ticket(self) -> ReviewPacket:
        """Execute the workflow for the packaged demo sample ticket."""
        return self.run_ticket(sample_ticket())
