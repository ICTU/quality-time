"""HQ metrics collector."""

from utilities.type import Responses, URL, Value
from .source_collector import SourceCollector


class HQ(SourceCollector):
    """HQ collector."""

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/json/metrics.json")

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        metric = [
            m for m in responses[0].json()["metrics"] if m["stable_metric_id"] == self._parameter("metric_id")][0]
        return str(metric["value"])
