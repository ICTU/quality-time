"""Metric collector that returns random values."""

import random
from typing import List

import requests

from utilities.type import Value
from .source_collector import LocalSourceCollector


class Random(LocalSourceCollector):
    """Random number metric collector."""
    min = 1
    max = 99
    total = 100

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(random.randint(self.min, self.max))  # nosec, random generator is not used for security purpose

    def _parse_source_responses_total(self, responses: List[requests.Response]) -> Value:
        return str(self.total)
