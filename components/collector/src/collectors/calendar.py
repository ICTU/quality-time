"""Calendar metric source."""

import io
from datetime import datetime
from typing import cast, List

import requests

from ..collector import Collector
from ..type import Parameter, URL


class CalendarSourceUpToDateness(Collector):
    """Collector class to get the number of days since a user-specified date."""

    def get_source_responses(self, api_url: URL, **parameters: Parameter) -> List[requests.Response]:
        """Return a random number as the response."""
        days = (datetime.now() - datetime.fromisoformat(cast(str, parameters.get("date", "")))).days
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(days), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return [response]
