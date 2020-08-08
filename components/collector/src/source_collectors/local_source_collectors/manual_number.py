"""Metric collector that returns a manually entered number."""

from collector_utilities.type import Responses
from base_collectors import LocalSourceCollector, SourceMeasurement


class ManualNumber(LocalSourceCollector):
    """Manual number metric collector."""

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        return SourceMeasurement(value=str(self._parameter("number")))
