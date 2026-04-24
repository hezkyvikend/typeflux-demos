from __future__ import annotations

from support_triage_yaml.domain import load_config
from support_triage_yaml.registry import inline_resolver


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
