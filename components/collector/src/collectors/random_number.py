"""Metric collector that returns random values."""

import io
import random
from typing import List

import requests

from ..collector import Collector
from ..type import URL


class Random(Collector):
    """Random number metric collector."""
    min = 1
    max = 99

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Return a random number as the response."""
        response = requests.Response()
        # Turn off security checks on the next line. The random number is not used for security/cryptography.
        response.raw = io.BytesIO(bytes(str(random.randint(self.min, self.max)), "utf-8"))  # nosec
        response.status_code = requests.status_codes.codes["OK"]
        return [response]
