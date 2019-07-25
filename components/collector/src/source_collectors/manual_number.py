"""Metric collector that returns a mnaually entered number."""

import io
from typing import List

import requests

from utilities.type import URL
from .source_collector import SourceCollector


class ManualNumber(SourceCollector):
    """Manual number metric collector."""

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Return a manually entered number as the response."""
        response = requests.Response()
        number = str(self.parameter("number"))
        response.raw = io.BytesIO(bytes(number, "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return [response]
