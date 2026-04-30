"""Small observers used by the support-triage tutorial."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from typeflux import StepEvent
from typeflux.observability.observer import NoOpObserver, Observer

from ..config import Settings


@dataclass
class LoggingObserver:
    """Log each Typeflux step event without coupling the workflow to logging."""

    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("support_triage_project.observer"))

    def on_event(self, event: StepEvent) -> None:
        if event.error is not None:
            self.logger.warning(
                "step=%s kind=%s attempt=%s elapsed_ms=%s error=%s",
                event.step_name,
                event.kind,
                event.attempt,
                event.elapsed_ms,
                event.error,
            )
            return

        self.logger.info(
            "step=%s kind=%s attempt=%s elapsed_ms=%s",
            event.step_name,
            event.kind,
            event.attempt,
            event.elapsed_ms,
        )


@dataclass
class RecordingObserver:
    """Test-friendly observer that stores emitted step events."""

    events: list[StepEvent] = field(default_factory=list)

    def on_event(self, event: StepEvent) -> None:
        self.events.append(event)


class _QuietLangfuseClient:
    """Adapter that avoids Langfuse's no-active-span context warning."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def get_current_trace_id(self) -> str | None:
        return None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


def observer_from_alias(alias: str | None, settings: Settings | None = None) -> Observer:
    """Resolve a workflow observer alias into a concrete Observer instance."""
    if alias in (None, "none", "noop"):
        return NoOpObserver()
    if alias == "logging":
        return LoggingObserver()
    if alias == "langfuse":
        from langfuse import Langfuse
        from typeflux.observability.langfuse import LangfuseObserver

        runtime_settings = settings or Settings()
        client = Langfuse(
            host=runtime_settings.langfuse_host,
            public_key=runtime_settings.langfuse_public_key,
            secret_key=runtime_settings.langfuse_secret_key,
        )
        return LangfuseObserver(client=_QuietLangfuseClient(client))
    raise ValueError(f"Unknown observer alias: {alias!r}")
