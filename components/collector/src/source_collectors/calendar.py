"""Calendar metric source."""

import io
from datetime import datetime
from typing import cast, List

import requests

from ..source_collectors.source_collector import SourceCollector
from ..utilities.type import URL


class CalendarSourceUpToDateness(SourceCollector):
    """Collector class to get the number of days since a user-specified date."""

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Return a random number as the response."""
        days = (datetime.now() - datetime.fromisoformat(cast(str, self.parameters.get("date", "")))).days
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(days), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return [response]
