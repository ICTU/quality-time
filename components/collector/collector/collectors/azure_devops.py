"""Azure Devops Server metric collector."""

import requests

from collector.collector import Collector
from collector.type import URL, Value


class AzureDevopsIssues(Collector):
    """Collector to get issues from Azure Devops Server."""
    request_method = "GET"

    def api_url(self, **parameters) -> URL:
        url = parameters.get("url")
        return URL(f"{url}/_apis/projects?api-version=5.0")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(response.json()["count"])
