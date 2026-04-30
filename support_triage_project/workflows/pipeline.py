"""The support-triage YAML workflow."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import as_file, files
from pathlib import Path
from typing import cast

from typeflux import InlineResolver, WorkflowSpec, load_from_yaml, run_workflow
from typeflux.observability.observer import NoOpObserver, Observer
from typeflux.providers.base import ModelProvider
from typeflux.registry.base import PromptResolver

from ..schemas import ReviewPacket, TicketInput

_WORKFLOW_YAML = files("support_triage_project.workflows").joinpath("support_triage.yaml")


@lru_cache(maxsize=1)
def _load_workflow() -> WorkflowSpec:
    with as_file(_WORKFLOW_YAML) as yaml_path:
        return load_from_yaml(Path(yaml_path))


SupportTriageWorkflow = _load_workflow()


def run(
    ticket: TicketInput,
    *,
    provider: ModelProvider,
    resolver: PromptResolver | None = None,
    observer: Observer | None = None,
) -> ReviewPacket:
    """Execute the support-triage workflow end to end."""
    result = run_workflow(
        SupportTriageWorkflow,
        ticket,
        resolver=resolver or InlineResolver(),
        provider=provider,
        observer=observer or NoOpObserver(),
    )
    return cast(ReviewPacket, result)
