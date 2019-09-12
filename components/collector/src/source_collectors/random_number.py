"""Metric collector that returns random values."""

import random
from http import HTTPStatus
from typing import List

import requests

from utilities.type import URL, Value
from .source_collector import SourceCollector


class Random(SourceCollector):
    """Random number metric collector."""
    min = 1
    max = 99
    total = 100

    def _get_source_responses(self, api_url: URL) -> List[requests.Response]:
        fake_response = requests.Response()  # Return a fake response so that the parse methods will be called
        fake_response.status_code = HTTPStatus.OK
        return [fake_response]

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(random.randint(self.min, self.max))  # nosec, random generator is not used for security purpose

    def _parse_source_responses_total(self, responses: List[requests.Response]) -> Value:
        return str(self.total)
