"""Jira metric collector."""

from typing import cast, List
from urllib.parse import quote

import requests

from utilities.type import Entities, URL, Value
from .source_collector import SourceCollector


class JiraBase(SourceCollector):
    """Base class for Jira collectors."""

    def api_url(self) -> URL:
        url = super().api_url()
        jql = quote(str(self.parameters.get("jql")))
        fields = self.fields()
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields={fields}&maxResults=500")

    def landing_url(self, responses: List[requests.Response]) -> URL:
        url = super().landing_url(responses)
        jql = quote(str(self.parameters.get("jql")))
        return URL(f"{url}/issues?jql={jql}")

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        url = self.parameters.get("url")
        return [dict(key=issue["id"], summary=issue["fields"]["summary"], url=f"{url}/browse/{issue['key']}")
                for issue in responses[0].json().get("issues", [])]

    def fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        return "summary"


class JiraIssues(JiraBase):
    """Collector to get issues from Jira."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(responses[0].json()["total"])


class JiraFieldSumBase(JiraBase):
    """Base class for collectors that sum a custom Jira field."""

    field_parameter = "subclass responsibility"
    entity_key = "subclass responsibility"

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        field = self.parameters[self.field_parameter]
        return str(round(sum(issue["fields"][field] for issue in responses[0].json()["issues"]
                             if issue["fields"][field] is not None)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        entities = super().parse_source_responses_entities(responses)
        field = self.parameters[self.field_parameter]
        for index, issue in enumerate(responses[0].json().get("issues", [])):
            entities[index][self.entity_key] = issue["fields"][field]
        return entities

    def fields(self) -> str:
        return super().fields() + "," + cast(str, self.parameters[self.field_parameter])


class JiraReadyUserStoryPoints(JiraFieldSumBase):
    """Collector to get ready user story points from Jira."""

    field_parameter = "story_points_field"
    entity_key = "points"


class JiraManualTestDuration(JiraFieldSumBase):
    """Collector to get manual test duration from Jira."""

    field_parameter = "manual_test_duration_field"
    entity_key = "duration"
