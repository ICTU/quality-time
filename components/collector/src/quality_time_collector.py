"""Measurement collector."""

import asyncio
import logging

# Make sure subclasses are registered
import metric_collectors  # pylint: disable=unused-import # lgtm [py/unused-import]
import source_collectors  # pylint: disable=unused-import # lgtm [py/unused-import]
from base_collectors import Collector


async def collect(log_level: int = None) -> None:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    await Collector().start()


if __name__ == "__main__":
    asyncio.run(collect(logging.WARNING))  # pragma: no cover
