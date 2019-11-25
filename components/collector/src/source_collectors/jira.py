"""Jira metric collector."""

from abc import ABC
from typing import cast, Dict, Optional, Union
from urllib.parse import quote

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Entity, Entities, Responses, URL, Value
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
        url = URL(str(self._parameter("url")))
        issues = responses[0].json().get("issues", [])
        return [self._create_entity(issue, url) for issue in issues if self._include_issue(issue)]

    def _create_entity(self, issue: Dict, url: URL) -> Entity:  # pylint: disable=no-self-use
        """Create an entity from a Jira issue."""
        return dict(key=issue["id"], summary=issue["fields"]["summary"], url=f"{url}/browse/{issue['key']}")

    def _include_issue(self, issue: Dict) -> bool:  # pylint: disable=no-self-use,unused-argument
        """Return whether this issue should be counted."""
        return True

    def _fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        return "summary"


class JiraIssues(JiraBase):
    """Collector to get issues from Jira."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(responses[0].json()["total"])


class JiraManualTestExecution(JiraBase):
    """Collector for the number of manual test cases that have not been executed recently enough."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _create_entity(self, issue: Dict, url: URL) -> Entity:
        entity = super()._create_entity(issue, url)
        entity["days_untested"] = str(self.__days_untested(issue))
        entity["desired_test_frequency"] = str(self.__desired_test_execution_frequency(issue))
        return entity

    def _include_issue(self, issue: Dict) -> bool:
        return self.__days_untested(issue) > self.__desired_test_execution_frequency(issue)

    def _fields(self) -> str:
        return super()._fields() + ",comment"

    @staticmethod
    def __days_untested(issue: Dict) -> int:
        """Return the days this issue has not been tested."""
        comment_dates = [comment["updated"] for comment in issue["fields"]["comment"]["comments"]]
        return days_ago(parse(max(comment_dates))) if comment_dates else 0

    def __desired_test_execution_frequency(self, issue: Dict) -> int:
        """Return the desired test frequency for this issue."""
        frequency = issue["fields"].get(self._parameter("manual_test_execution_frequency_field"))
        return int(
            round(float(frequency)) if frequency else str(self._parameter("manual_test_execution_frequency_default")))


class JiraFieldSumBase(JiraBase):
    """Base class for collectors that sum a custom Jira field."""

    field_parameter = "subclass responsibility"
    entity_key = "subclass responsibility"

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        entities = self._parse_source_responses_entities(responses)
        return str(round(sum(float(entity[self.entity_key]) for entity in entities)))

    def _create_entity(self, issue: Dict, url: URL) -> Entity:
        entity = super()._create_entity(issue, url)
        entity[self.entity_key] = self.__value_of_field_to_sum(issue)
        return entity

    def _include_issue(self, issue: Dict) -> bool:
        return self.__value_of_field_to_sum(issue) is not None

    def _fields(self) -> str:
        return super()._fields() + "," + cast(str, self._parameter(self.field_parameter))

    def __value_of_field_to_sum(self, issue: Dict) -> Optional[Union[int, float]]:
        """Return the value of the issue field that this collectors is to sum."""
        return issue["fields"][self._parameter(self.field_parameter)]


class JiraReadyUserStoryPoints(JiraFieldSumBase):
    """Collector to get ready user story points from Jira."""

    field_parameter = "story_points_field"
    entity_key = "points"


class JiraManualTestDuration(JiraFieldSumBase):
    """Collector to get manual test duration from Jira."""

    field_parameter = "manual_test_duration_field"
    entity_key = "duration"
