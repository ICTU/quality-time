"""Axe-core accessibility time passed collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.type import Response


class AxeCoreTimePassed(JSONFileSourceCollector, TimePassedCollector):
    """Collector to get the time passed since the latest Axe-core JSON reports."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        json = await response.json(content_type=None)
        if isinstance(json, list):
            json = json[0]  # The JSON consists of several Axe-core JSONs in a list, assume they have the same timestamp
        return parse(json["timestamp"])
