"""Gatling source up-to-dateness collector."""

from datetime import datetime

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_fromtimestamp, now
from collector_utilities.type import Response
from model import SourceResponses

from .base import GatlingLogCollector


class GatlingSourceUpToDateness(GatlingLogCollector, TimePassedCollector):
    """Collector for the performance test report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the start date time of the test from the response."""
        timestamps = await self._timestamps(SourceResponses(responses=[response]))
        return datetime_fromtimestamp(min(timestamps) / 1000.0) if timestamps else now()
