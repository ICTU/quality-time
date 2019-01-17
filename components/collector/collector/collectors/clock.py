"""Clock metric source."""

import requests

from collector.collector import Collector
from collector.type import Measurement


class ClockTime(Collector):
    """Clock metric collector."""
    name = "Clock"

    def parse_source_response(self, response: requests.Response) -> Measurement:
        return Measurement(response.json()["unixtime"])
