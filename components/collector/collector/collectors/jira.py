"""Jira metric collector."""

from urllib.parse import quote

import requests

from collector.collector import Collector
from collector.type import URL, Value


class JiraIssues(Collector):
    """Collector to get issues from Jira."""
    def api_url(self, **parameters) -> URL:
        url = parameters.get("url")
        jql = quote(parameters.get("jql"))
        return URL(f"{url}/rest/api/2/search?jql={jql}")

    def landing_url(self, **parameters) -> URL:
        url = parameters.get("url")
        jql = quote(parameters.get("jql"))
        return URL(f"{url}/issues?jql={jql}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(response.json()["total"])
