"""Jira metric collector."""

from typing import Optional
from urllib.parse import quote

import requests

from ..collector import Collector
from ..type import Entities, URL, Value


class JiraIssues(Collector):
    """Collector to get issues from Jira."""

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        jql = quote(str(parameters.get("jql")))
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields=summary")

    def landing_url(self, response: Optional[requests.Response], **parameters) -> URL:
        url = super().landing_url(response, **parameters)
        jql = quote(str(parameters.get("jql")))
        return URL(f"{url}/issues?jql={jql}")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(response.json()["total"])

    def parse_source_response_entities(self, response: requests.Response, **parameters) -> Entities:
        url = parameters.get("url")
        return [dict(key=issue["id"], summary=issue["fields"]["summary"],
                     url=f"{url}/browse/{issue['key']}") for issue in response.json().get("issues", [])]
