"""Gatling performancetest duration collector."""

from typing import TYPE_CHECKING

from collector_utilities.date_time import parse_duration

from .base import GatlingHTMLCollector

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, SourceResponses


class GatlingPerformanceTestDuration(GatlingHTMLCollector):
    """Collector for the performance test duration."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to parse the duration from the HTML."""
        return str(
            sum([parse_duration(await self.simulation_information(response, "Duration")) for response in responses])
        )
