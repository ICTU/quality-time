"""Metric collector that returns a manually entered number."""

from base_collectors import LocalSourceCollector, SourceMeasurement, SourceResponses


class ManualNumber(LocalSourceCollector):
    """Manual number metric collector."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        return SourceMeasurement(value=str(self._parameter("number")))
