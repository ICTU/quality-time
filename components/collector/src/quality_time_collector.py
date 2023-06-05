"""Measurement collector."""

import asyncio
import logging
from typing import NoReturn

# Make sure subclasses are registered
import metric_collectors  # noqa: F401
import source_collectors  # noqa: F401
from base_collectors import Collector, config


async def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(config.LOG_LEVEL)
    await Collector().start()


if __name__ == "__main__":
    asyncio.run(collect())  # pragma: no cover
