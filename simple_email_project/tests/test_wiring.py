from __future__ import annotations

from simple_email_project.registry import inline_resolver


def test_packaged_prompts_are_available() -> None:
    resolver = inline_resolver()

    assert sorted(resolver.prompts.keys()) == [
        ("email-classify-intent", "production"),
        ("email-draft-reply", "production"),
    ]
