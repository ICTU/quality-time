"""Measurement collector."""

import asyncio
import logging
from typing import NoReturn

from shared.initialization.database import database_connection
from shared.utils.env import getenv, loadenv

# Make sure subclasses are registered
import metric_collectors  # noqa: F401
import source_collectors  # noqa: F401
from base_collectors import Collector


async def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    loadenv(".env", "default.env")
    log_level = getenv("COLLECTOR_LOG_LEVEL")
    logger = logging.getLogger()
    logger.setLevel(log_level)
    await Collector(database_connection()).start()


if __name__ == "__main__":
    asyncio.run(collect())  # pragma: no cover
