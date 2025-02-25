"""Gatling performancetest duration collector."""

from collector_utilities.type import Value
from model import Entities, SourceResponses

from .base import GatlingLogCollector


class GatlingPerformanceTestDuration(GatlingLogCollector):
    """Collector for the performance test duration."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to parse the timestamps from the log and calculate the duration in minutes."""
        timestamps = await self._timestamps(responses)
        return str(round((max(timestamps) - min(timestamps)) / 60_000)) if timestamps else "0"
