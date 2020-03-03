"""Metric collector that returns a mnaually entered number."""

from typing import Tuple

from collector_utilities.type import Entities, Responses, Value
from .source_collector import LocalSourceCollector


class ManualNumber(LocalSourceCollector):
    """Manual number metric collector."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        return str(self._parameter("number")), "100", []
