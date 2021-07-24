"""Measurement collector."""

import asyncio
import logging

# Make sure subclasses are registered
import metric_collectors  # lgtm [py/unused-import], pylint: disable=unused-import
import source_collectors  # lgtm [py/unused-import], pylint: disable=unused-import
from base_collectors import Collector


async def collect(log_level: int = None) -> None:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    await Collector().start()


if __name__ == "__main__":
    asyncio.run(collect(logging.INFO), debug=True)  # pragma: no cover
