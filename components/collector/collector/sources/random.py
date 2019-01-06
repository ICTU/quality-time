"""Metric source that returns random values."""

import io
import random

import requests

from collector.source import Source
from collector.type import URL


class RandomViolations(Source):
    """Random number of violations metric source."""
    name = "Random"

    def get_source_response(self, url: URL) -> requests.Response:
        """Return a random number as the response."""
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(random.randint(0, 50)), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return response
