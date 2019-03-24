"""HQ metrics collector."""

from urllib.parse import urljoin

import requests

from ..collector import Collector
from ..type import URL, Value


class HQ(Collector):
    """HQ collector."""

    def api_url(self, **parameters) -> URL:
        return URL(urljoin(parameters.get("url", "") + "/", "json/metrics.json"))

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        metric = [m for m in response.json()["metrics"] if m["stable_metric_id"] == parameters.get("metric_id")][0]
        return metric["value"]


class HQDuplicatedLines(HQ):
    """HQ duplicated lines collector."""


class HQViolations(HQ):
    """HQ violations collector."""


class HQFailedJobs(HQ):
    """HQ failed jobs collector."""


class HQFailedTests(HQ):
    """HQ failed tests collector."""


class HQIssues(HQ):
    """HQ issues collector."""


class HQNCLOC(HQ):
    """HQ non-commented lines of code collector."""


class HQUnusedJobs(HQ):
    """HQ unused jobs collector."""
