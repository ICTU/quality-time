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
        value = random.randint(self.MIN, self.MAX)  # nosec, random generator is not used for security purpose
        return SourceMeasurement(value=str(value))
