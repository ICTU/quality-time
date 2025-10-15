"""Axe-core accessibility source up-to-dateness collector."""

from typing import TYPE_CHECKING

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.date_time import parse_datetime

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class AxeCoreSourceUpToDateness(JSONFileSourceCollector, TimePassedCollector):
    """Collector to get the source up-to-dateness of Axe-core JSON reports."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        json = await response.json(content_type=None)
        if isinstance(json, list):
            json = json[0]  # The JSON consists of several Axe-core JSONs in a list, assume they have the same timestamp
        return parse_datetime(json["timestamp"])
