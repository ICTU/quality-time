"""JMeter CSV source up-to-dateness collector."""

from typing import TYPE_CHECKING

from shared.utils.date_time import now

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_from_timestamp
from model import SourceResponses

from .base import JMeterCSVCollector

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class JMeterCSVSourceUpToDateness(JMeterCSVCollector, TimePassedCollector):
    """Collector for the performance test report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the start date time of the test from the response."""
        timestamps = await self._timestamps(SourceResponses(responses=[response]))
        return datetime_from_timestamp(min(timestamps)) if timestamps else now()
