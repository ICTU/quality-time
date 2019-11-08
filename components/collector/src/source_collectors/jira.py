"""Jira metric collector."""

from abc import ABC
from datetime import datetime
from typing import cast, List
from urllib.parse import quote

from collector_utilities.type import Entities, Responses, URL, Value
from collector_utilities.functions import days_ago
from .source_collector import SourceCollector


class JiraBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Jira collectors."""

    def _api_url(self) -> URL:
        url = super()._api_url()
        jql = quote(str(self._parameter("jql")))
        fields = self._fields()
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields={fields}&maxResults=500")

    def _landing_url(self, responses: Responses) -> URL:
        url = super()._landing_url(responses)
        jql = quote(str(self._parameter("jql")))
        return URL(f"{url}/issues?jql={jql}")

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        url = self._parameter("url")
        return [dict(key=issue["id"], summary=issue["fields"]["summary"], url=f"{url}/browse/{issue['key']}")
                for issue in responses[0].json().get("issues", [])]

    def _fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        return "summary"


class JiraIssues(JiraBase):
    """Collector to get issues from Jira."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(responses[0].json()["total"])


class JiraFieldSumBase(JiraBase):
    """Base class for collectors that sum a custom Jira field."""

    field_parameter = "subclass responsibility"
    entity_key = "subclass responsibility"

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        field = self._parameter(self.field_parameter)
        return str(round(sum(issue["fields"][field] for issue in responses[0].json()["issues"]
                             if issue["fields"][field] is not None)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        entities = super()._parse_source_responses_entities(responses)
        field = self._parameter(self.field_parameter)
        for index, issue in enumerate(responses[0].json().get("issues", [])):
            entities[index][self.entity_key] = issue["fields"][field]
        return entities

    def _fields(self) -> str:
        return super()._fields() + "," + cast(str, self._parameter(self.field_parameter))


class JiraReadyUserStoryPoints(JiraFieldSumBase):
    """Collector to get ready user story points from Jira."""

    field_parameter = "story_points_field"
    entity_key = "points"


class JiraManualTestDuration(JiraFieldSumBase):
    """Collector to get manual test duration from Jira."""

    field_parameter = "manual_test_duration_field"
    entity_key = "duration"

class JiraManualTestExecutionFrequency(JiraFieldSumBase):
    """Collector to get manual test execution from Jira."""

    field_parameter = "manual_test_execution_frequency_field"
    entity_key = "days"

    # @functools.lru_cache(maxsize=2048)
    def _parse_source_responses(self, responses: Responses) -> List:
        field = self._parameter(self.field_parameter)
        param = self._parameter("manual_test_default_frequency_field")
        default_frequency = int(param[0] if isinstance(param, list) else param)

        def __frequency(issue_fields, default: int) -> int:
            return int(issue_fields[field] if field in issue_fields and issue_fields[field] is not None else default)

        def __touched_days_ago(issue_fields) -> int:
            max_date_str = max([comment["updated"] for comment in issue_fields["comment"]["comments"]])
            split_date = max_date_str[:max_date_str.find('T')].split('-') if max_date_str else [0, 0, 0]
            return days_ago(datetime(int(split_date[0]), int(split_date[1]), int(split_date[2])))

        return [issue  for issue in responses[0].json()["issues"]
                if __frequency(issue["fields"], default_frequency) <= __touched_days_ago(issue["fields"])]

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._parse_source_responses(responses)))


    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        url = self._parameter("url")
        ltc_issues = self._parse_source_responses(responses)
        return [dict(key=issue["id"], summary=issue["fields"]["summary"], url=f"{url}/browse/{issue['key']}")
                for issue in ltc_issues]

    def _fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        return "*all"
