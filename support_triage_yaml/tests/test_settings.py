from __future__ import annotations

from support_triage_yaml.config import Settings


def test_settings_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.anthropic_api_key == "test-key"
    assert settings.anthropic_model == "claude-test"
    assert settings.log_level == "DEBUG"
