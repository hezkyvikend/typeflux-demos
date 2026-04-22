"""CLI entry point for the file-backed InlineResolver + Anthropic demo."""

from __future__ import annotations

import argparse
import logging
import sys

from .app import SupportTriageApp
from .config import Settings
from .schemas import ReviewPacket


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Typeflux support-triage demo using local prompt files and Anthropic."
    )
    parser.parse_args(argv)

    settings = Settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(levelname)s %(name)s: %(message)s",
    )

    packet: ReviewPacket = SupportTriageApp.from_settings(settings).run_sample_ticket()
    print(packet.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
