"""Metric collector that returns a manually entered number."""

from typing import TYPE_CHECKING

from base_collectors import SourceCollector

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, SourceResponses


class ManualNumber(SourceCollector):
    """Manual number collector."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to return the user-supplied manual number."""
        return str(self._parameter("number"))

    async def _parse_total(self, responses: SourceResponses, entities: Entities) -> Value:
        """Override to return the total, which is always 100 to support metrics with a percentage scale."""
        return "100"
