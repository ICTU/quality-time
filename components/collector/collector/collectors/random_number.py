"""Metric collector that returns random values."""

import io
import random

import requests

from collector.collector import Collector
from collector.type import URL


class RandomViolations(Collector):
    """Random number of violations metric collector."""
    name = "Random"

    def get_source_response(self, url: URL) -> requests.Response:
        """Return a random number as the response."""
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(random.randint(0, 50)), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return response
