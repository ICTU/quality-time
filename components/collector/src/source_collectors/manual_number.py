"""Metric collector that returns a mnaually entered number."""

import io
from typing import List

import requests

from ..source_collector import SourceCollector
from ..type import URL


class ManualNumber(SourceCollector):
    """Manual number metric collector."""

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Return a manually entered number as the response."""
        response = requests.Response()
        number = self.parameters.get("number", 0)
        response.raw = io.BytesIO(bytes(str(number), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return [response]
