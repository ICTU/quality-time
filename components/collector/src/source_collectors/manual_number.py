"""Metric collector that returns a mnaually entered number."""

from typing import List

import requests

from utilities.type import Value
from .source_collector import LocalSourceCollector


class ManualNumber(LocalSourceCollector):
    """Manual number metric collector."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(self._parameter("number"))
