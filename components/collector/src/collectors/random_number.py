"""Metric collector that returns random values."""

import io
import random
from typing import List

import requests

from ..collector import Collector
from ..type import Parameter, URL


class Random(Collector):
    """Random number metric collector."""
    min = 0
    max = 50

    def get_source_responses(self, api_url: URL, **parameters: Parameter) -> List[requests.Response]:
        """Return a random number as the response."""
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(random.randint(self.min, self.max)), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return [response]
