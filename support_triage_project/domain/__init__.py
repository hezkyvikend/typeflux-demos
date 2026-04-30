"""Deterministic business rules and configuration for support triage."""

from .rules import COMPLIANCE_FOOTER, DomainConfig, is_within_business_hours, load_config, redact_pii

__all__ = [
    "COMPLIANCE_FOOTER",
    "DomainConfig",
    "is_within_business_hours",
    "load_config",
    "redact_pii",
]

