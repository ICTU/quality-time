"""Measurement collector."""

import asyncio
import logging

from base_collectors import MetricsCollector
# Make sure subclasses are registered
from source_collectors import *  # lgtm [py/polluting-import] pylint: disable=unused-wildcard-import,wildcard-import


async def collect(log_level: int = None) -> None:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    await MetricsCollector().start()


if __name__ == "__main__":
    asyncio.run(collect(logging.INFO), debug=True)  # pragma: nocover
