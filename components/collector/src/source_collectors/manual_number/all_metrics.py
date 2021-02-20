"""Metric collector that returns a manually entered number."""

from base_collectors import SourceCollector
from source_model import SourceMeasurement, SourceResponses


class ManualNumber(SourceCollector):
    """Manual number collector."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to return the user-supplied manual number."""
        return SourceMeasurement(value=str(self._parameter("number")))
