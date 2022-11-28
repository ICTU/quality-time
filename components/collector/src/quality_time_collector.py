"""Measurement collector."""

import asyncio
import logging
import os
from typing import NoReturn

# Make sure subclasses are registered
import metric_collectors  # pylint: disable=unused-import # lgtm [py/unused-import]
import source_collectors  # pylint: disable=unused-import # lgtm [py/unused-import]
from base_collectors import Collector


async def collect(log_level: int | str | None = None) -> NoReturn:
    """Collect the measurements indefinitely."""
    if log_level is None:
        log_level = str(os.getenv("COLLECTOR_LOG_LEVEL", "WARNING"))
    logging.getLogger().setLevel(log_level)
    await Collector().start()


if __name__ == "__main__":
    asyncio.run(collect())  # pragma: no cover
