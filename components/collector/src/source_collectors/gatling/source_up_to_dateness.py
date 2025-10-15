"""Gatling source up-to-dateness collector."""

from typing import TYPE_CHECKING

from shared.utils.date_time import now

from base_collectors import TimePassedCollector
from collector_utilities.date_time import parse_datetime

from .base import GatlingHTMLCollector

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class GatlingSourceUpToDateness(GatlingHTMLCollector, TimePassedCollector):
    """Collector for the performance test report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the start date time of the test from the response."""
        if datetime_str := await self.simulation_information(response, "Date"):
            return parse_datetime(datetime_str)
        return now()
