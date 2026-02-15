"""Measurement collector."""

import asyncio
import logging
from typing import NoReturn

from rich.logging import RichHandler

from shared.initialization.database import get_database, mongo_client

# Make sure subclasses are registered
import metric_collectors  # noqa: F401
import source_collectors  # noqa: F401
from base_collectors import Collector, config


async def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S", format="%(message)s", handlers=[RichHandler()])
    logging.getLogger().setLevel(config.LOG_LEVEL)
    with mongo_client() as client:
        await Collector(get_database(client)).start()


if __name__ == "__main__":
    asyncio.run(collect())  # pragma: no cover
