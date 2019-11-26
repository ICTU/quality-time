"""Metric collector that returns random values."""

import random
from typing import Tuple

from collector_utilities.type import Entities, Responses, Value
from .source_collector import LocalSourceCollector


class Random(LocalSourceCollector):
    """Random number metric collector."""
    min = 1
    max = 99
    total = 100

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        value = random.randint(self.min, self.max)  # nosec, random generator is not used for security purpose
        return str(value), str(self.total), []
