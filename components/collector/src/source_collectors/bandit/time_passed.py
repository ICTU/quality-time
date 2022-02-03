"""Bandit source time passed collector."""

from datetime import datetime

from dateutil.parser import parse

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.type import Response


class BanditTimePassed(JSONFileSourceCollector, TimePassedCollector):
    """Collector for the time passed since the latest Bandit report."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp."""
        return parse((await response.json(content_type=None))["generated_at"])
