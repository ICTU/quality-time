"""Metric collector that returns random values."""

import random
from typing import Final

from base_collectors import SourceCollector
from collector_utilities.type import Value
from source_model import SourceResponses


class Random(SourceCollector):
    """Random number metric collector."""

    MIN: Final[int] = 1
    MAX: Final[int] = 99

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to return a random number."""
        return str(random.randint(self.MIN, self.MAX))  # noqa: DUO102, # nosec, random generator not used for security
