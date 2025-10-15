"""JMeter CSV performancetest duration collector."""

from typing import TYPE_CHECKING

from .base import JMeterCSVCollector

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, SourceResponses


class JMeterCSVPerformanceTestDuration(JMeterCSVCollector):
    """Collector for the performance test duration."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to parse the timestamps from the samples and calculate the duration in minutes."""
        timestamps = await self._timestamps(responses)
        return str(round((max(timestamps) - min(timestamps)) / 60_000)) if timestamps else "0"
