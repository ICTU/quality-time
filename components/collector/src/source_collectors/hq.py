"""HQ metrics collector."""

from typing import List

import requests

from ..source_collector import SourceCollector
from ..type import URL, Value


class HQ(SourceCollector):
    """HQ collector."""

    def api_url(self) -> URL:
        return URL(f"{super().api_url()}/json/metrics.json")

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        metric = [
            m for m in responses[0].json()["metrics"] if m["stable_metric_id"] == self.parameters.get("metric_id")][0]
        return metric["value"]
