"""
Structured logging setup. Every agent/service should use
`logging.getLogger(__name__)` rather than print() -- this is what feeds
the Agent Activity Log (spec section 22) once the orchestrator exists.
"""
import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
