"""Measurement collector."""

import asyncio
from typing import NoReturn

from shared.initialization.database import get_database, mongo_client
from shared.utils.log import init_logging

# Make sure subclasses are registered
import metric_collectors  # noqa: F401
import source_collectors  # noqa: F401
from base_collectors import Collector, config


async def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    init_logging(config.LOG_LEVEL)
    with mongo_client() as client:
        await Collector(get_database(client)).start()


if __name__ == "__main__":
    asyncio.run(collect())  # pragma: no cover
