"""Metric collector that returns a manually entered number."""

from base_collectors import SourceCollector
from collector_utilities.type import Value
from model import SourceResponses


class ManualNumber(SourceCollector):
    """Manual number collector."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to return the user-supplied manual number."""
        return str(self._parameter("number"))
