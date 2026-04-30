"""The simple email YAML workflow."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import as_file, files
from pathlib import Path
from typing import cast

from typeflux import InlineResolver, WorkflowSpec, load_from_yaml, run_workflow
from typeflux.observability.observer import NoOpObserver, Observer
from typeflux.providers.base import ModelProvider
from typeflux.registry.base import PromptResolver

from ..schemas import DraftReply, EmailInput

_WORKFLOW_YAML = files("simple_email_project.workflows").joinpath("email_reply.yaml")


@lru_cache(maxsize=1)
def _load_workflow() -> WorkflowSpec:
    with as_file(_WORKFLOW_YAML) as yaml_path:
        return load_from_yaml(Path(yaml_path))


EmailReplyWorkflow = _load_workflow()


def run(
    email: EmailInput,
    *,
    provider: ModelProvider,
    resolver: PromptResolver | None = None,
    observer: Observer | None = None,
) -> DraftReply:
    """Run the email classification and reply workflow."""
    result = run_workflow(
        EmailReplyWorkflow,
        email,
        resolver=resolver or InlineResolver(),
        provider=provider,
        observer=observer or NoOpObserver(),
    )
    # run_workflow is generic over any workflow. This YAML's final step returns
    # DraftReply, so the cast teaches static type checkers what runtime
    # validation has already enforced.
    return cast(DraftReply, result)
