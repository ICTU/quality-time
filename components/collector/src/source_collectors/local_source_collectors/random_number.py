"""Metric collector that returns random values."""

import random
from typing import Final

from collector_utilities.type import Responses
from base_collectors import LocalSourceCollector, SourceMeasurement


class Random(LocalSourceCollector):
    """Random number metric collector."""
    MIN: Final[int] = 1
    MAX: Final[int] = 99

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        value = random.randint(self.MIN, self.MAX)  # nosec, random generator is not used for security purpose
        return SourceMeasurement(str(value))
