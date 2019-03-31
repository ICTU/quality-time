"""HQ metrics collector."""

import requests

from ..collector import Collector
from ..type import URL, Value


class HQ(Collector):
    """HQ collector."""

    def api_url(self, **parameters) -> URL:
        return URL(f"{super().api_url(**parameters)}/json/metrics.json")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        metric = [m for m in response.json()["metrics"] if m["stable_metric_id"] == parameters.get("metric_id")][0]
        return metric["value"]
