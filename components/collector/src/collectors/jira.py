"""Jira metric collector."""

from typing import List
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

    def landing_url(self, responses: List[requests.Response], **parameters) -> URL:
        url = super().landing_url(responses, **parameters)
        jql = quote(str(parameters.get("jql")))
        return URL(f"{url}/issues?jql={jql}")

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters) -> Value:
        return str(sum(int(response.json()["total"]) for response in responses))

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters) -> Entities:
        url = parameters.get("url")
        return [dict(key=issue["id"], summary=issue["fields"]["summary"], url=f"{url}/browse/{issue['key']}")
                for response in responses for issue in response.json().get("issues", [])]
