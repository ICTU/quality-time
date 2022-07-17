"""Measurement collector."""

import asyncio
import logging

from shared_data_model import DATA_MODEL_JSON

# Make sure subclasses are registered
import metric_collectors  # pylint: disable=unused-import # lgtm [py/unused-import]
import source_collectors  # pylint: disable=unused-import # lgtm [py/unused-import]
from base_collectors import Collector


async def collect(data_model, log_level: int = None) -> None:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    await Collector(data_model).start()


if __name__ == "__main__":
    asyncio.run(collect(DATA_MODEL_JSON, logging.INFO), debug=True)  # pragma: no cover
