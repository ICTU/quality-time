"""Grafana k6 performancetest duration collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.exceptions import CollectorError

from .json_types import SummaryJSON

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, SourceResponses


class GrafanaK6PerformanceTestDuration(JSONFileSourceCollector):
    """Collector for the performance test duration."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to parse the performance test durations from the responses and return the sum in minutes."""
        duration = 0.0
        for response in responses:
            json = await response.json(content_type=None)
            try:
                duration += cast(SummaryJSON, json)["state"]["testRunDurationMs"]
            except KeyError as error:
                message = 'Could not find an object {"state": {"testRunDurationMs": value}} in summary.json.'
                raise CollectorError(message) from error
        return str(round(duration / 60_000))
