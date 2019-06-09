"""Jira metric collector."""

from typing import List
from urllib.parse import quote

import requests

from ..collector import Collector
from ..type import Entities, URL, Value


class JiraBase(Collector):
    """Base class for Jira collectors."""

    def api_url(self, **parameters) -> URL:
        url = super().api_url(**parameters)
        jql = quote(str(parameters.get("jql")))
        fields = self.fields(**parameters)
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields={fields}&maxResults=500")

    def landing_url(self, responses: List[requests.Response], **parameters) -> URL:
        url = super().landing_url(responses, **parameters)
        jql = quote(str(parameters.get("jql")))
        return URL(f"{url}/issues?jql={jql}")

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters) -> Entities:
        url = parameters.get("url")
        return [dict(key=issue["id"], summary=issue["fields"]["summary"], url=f"{url}/browse/{issue['key']}")
                for issue in responses[0].json().get("issues", [])]

    def fields(self, **parameters) -> str:  # pylint: disable=unused-argument,no-self-use
        """Return the fields to get from Jira."""
        return "summary"


class JiraIssues(JiraBase):
    """Collector to get issues from Jira."""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters) -> Value:
        return str(responses[0].json()["total"])


class JiraReadyUserStoryPoints(JiraBase):
    """Collector to get ready user story points from Jira."""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters) -> Value:
        story_points_field = parameters["story_points_field"]
        return str(round(sum(issue["fields"][story_points_field] for issue in responses[0].json()["issues"]
                             if issue["fields"][story_points_field] is not None)))

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters) -> Entities:
        entities = super().parse_source_responses_entities(responses, **parameters)
        story_points_field = parameters["story_points_field"]
        for index, issue in enumerate(responses[0].json().get("issues", [])):
            entities[index]["points"] = issue["fields"][story_points_field]
        return entities

    def fields(self, **parameters) -> str:
        return super().fields(**parameters) + "," + parameters["story_points_field"]
