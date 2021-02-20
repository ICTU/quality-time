"""Metric collector that returns random values."""

import random
from typing import Final

from base_collectors import SourceCollector
from source_model import SourceMeasurement, SourceResponses


class Random(SourceCollector):
    """Random number metric collector."""

    MIN: Final[int] = 1
    MAX: Final[int] = 99

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to return a random number."""
        value = random.randint(self.MIN, self.MAX)  # noqa: DUO102, # nosec, random generator is not used for security
        return SourceMeasurement(value=str(value))
