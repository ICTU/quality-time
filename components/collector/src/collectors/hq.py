"""HQ metrics collector."""

from typing import List

import requests

from ..collector import Collector
from ..type import Parameter, URL, Value


class HQ(Collector):
    """HQ collector."""

    def api_url(self, **parameters: Parameter) -> URL:
        return URL(f"{super().api_url(**parameters)}/json/metrics.json")

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        metric = [m for m in responses[0].json()["metrics"] if m["stable_metric_id"] == parameters.get("metric_id")][0]
        return metric["value"]
