"""Metric collector that returns a mnaually entered number."""

from collector_utilities.type import Responses, Value
from .source_collector import LocalSourceCollector


class ManualNumber(LocalSourceCollector):
    """Manual number metric collector."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(self._parameter("number"))
