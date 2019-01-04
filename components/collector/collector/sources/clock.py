"""Clock metric source."""

import requests

from collector.source import Source
from collector.type import Measurement


class ClockTime(Source):
    """Clock metric source."""
    name = "Clock"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["unixtime"])
