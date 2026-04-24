"""Business rules for the support-triage pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, time, tzinfo
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import TypedDict, cast
from zoneinfo import ZoneInfo

import yaml


class _BusinessHoursYAML(TypedDict):
    timezone: str
    start: str
    end: str


class _OnCallYAML(TypedDict):
    primary: str
    secondary: str


class _DomainYAML(TypedDict):
    teams: list[str]
    on_call: _OnCallYAML
    business_hours: _BusinessHoursYAML


@dataclass(frozen=True)
class DomainConfig:
    """Validated view of ``domain.yaml``."""

    teams: frozenset[str]
    on_call_primary: str
    on_call_secondary: str
    business_hours_start: time
    business_hours_end: time
    business_hours_tz: tzinfo


DEFAULT_CONFIG_PATH: Traversable = files("support_triage_yaml.domain").joinpath("domain.yaml")


def load_config(path: Traversable = DEFAULT_CONFIG_PATH) -> DomainConfig:
    """Parse ``domain.yaml`` into a validated ``DomainConfig``."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping, got {type(raw).__name__}")

    for key in ("teams", "on_call", "business_hours"):
        if key not in raw:
            raise ValueError(f"{path}: missing required key '{key}'")

    data = cast(_DomainYAML, raw)
    teams = data["teams"]
    if not teams or not all(isinstance(team, str) for team in teams):
        raise ValueError(f"{path}: 'teams' must be a non-empty list of strings")

    business_hours = data["business_hours"]
    try:
        start = time.fromisoformat(business_hours["start"])
        end = time.fromisoformat(business_hours["end"])
    except (KeyError, ValueError) as exc:
        raise ValueError(f"{path}: invalid business_hours time format") from exc

    return DomainConfig(
        teams=frozenset(teams),
        on_call_primary=data["on_call"]["primary"],
        on_call_secondary=data["on_call"]["secondary"],
        business_hours_start=start,
        business_hours_end=end,
        business_hours_tz=ZoneInfo(business_hours["timezone"]),
    )


def is_within_business_hours(now: datetime, cfg: DomainConfig) -> bool:
    """Return True when ``now`` falls within configured weekday business hours."""
    if now.tzinfo is None:
        now = now.replace(tzinfo=ZoneInfo("UTC"))
    local = now.astimezone(cfg.business_hours_tz)
    if local.weekday() >= 5:
        return False
    current = local.time()
    return cfg.business_hours_start <= current < cfg.business_hours_end


_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)")
_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")

_REDACTIONS = (
    (_EMAIL_RE, "[EMAIL]"),
    (_PHONE_RE, "[PHONE]"),
    (_CARD_RE, "[CARD]"),
)


def redact_pii(text: str) -> tuple[str, int]:
    """Replace email, phone, and card-like strings with placeholders."""
    redacted = text
    total = 0
    for pattern, placeholder in _REDACTIONS:
        redacted, count = pattern.subn(placeholder, redacted)
        total += count
    return redacted, total


COMPLIANCE_FOOTER = (
    "\n\n---\n"
    "This reply was drafted with AI assistance and may be reviewed before "
    "sending. For billing inquiries, you may also contact support@example.com."
)
