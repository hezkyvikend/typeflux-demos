from __future__ import annotations

from support_triage_project.domain import load_config
from support_triage_project.observers.logging_observer import _QuietLangfuseClient
from support_triage_project.registry import inline_resolver, langfuse_resolver
from support_triage_project.workflows.pipeline import SupportTriageWorkflow


def test_packaged_domain_config_loads() -> None:
    cfg = load_config()
    assert "billing" in cfg.teams
    assert cfg.on_call_primary == "alice-chen"


def test_packaged_prompts_are_available() -> None:
    resolver = inline_resolver()
    assert sorted(resolver.prompts.keys()) == [
        ("triage-classify", "production"),
        ("triage-draft", "production"),
        ("triage-package", "production"),
        ("triage-route", "production"),
    ]


def test_langfuse_resolver_wires_shared_settings(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_HOST", "https://example.langfuse.test")

    resolver = langfuse_resolver()

    assert resolver.public_key == "pk-test"
    assert resolver.secret_key == "sk-test"
    assert resolver.host == "https://example.langfuse.test"


def test_workflow_aliases_provider_and_registry() -> None:
    assert SupportTriageWorkflow.provider == "anthropic"
    assert SupportTriageWorkflow.registry == "langfuse"
    assert SupportTriageWorkflow.observer == "langfuse"


def test_quiet_langfuse_client_does_not_probe_current_context() -> None:
    class _FakeLangfuseClient:
        flushed = False

        def get_current_trace_id(self) -> str:
            raise AssertionError("adapter should not call the wrapped context probe")

        def flush(self) -> None:
            self.flushed = True

    client = _FakeLangfuseClient()
    adapter = _QuietLangfuseClient(client)

    assert adapter.get_current_trace_id() is None
    adapter.flush()
    assert client.flushed is True
