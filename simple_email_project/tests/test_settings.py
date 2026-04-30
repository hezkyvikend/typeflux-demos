from __future__ import annotations

from simple_email_project.config import Settings


def test_settings_read_openai_values(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")

    settings = Settings()

    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "gpt-test"
