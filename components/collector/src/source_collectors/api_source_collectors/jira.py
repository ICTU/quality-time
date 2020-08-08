"""Jira metric collector."""

from datetime import datetime
from typing import cast, Dict, List, Optional, Union

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Entity, Responses, URL
from base_collectors import SourceCollector, SourceMeasurement


class JiraIssues(SourceCollector):
    """Jira collector for issues."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field_ids = {}

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        jql = str(self._parameter("jql", quote=True))
        fields = self._fields()
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields={fields}&maxResults=500")

    async def _landing_url(self, responses: Responses) -> URL:
        url = await super()._landing_url(responses)
        jql = str(self._parameter("jql", quote=True))
        return URL(f"{url}/issues/?jql={jql}")

    def _parameter(self, parameter_key: str, quote: bool = False) -> Union[str, List[str]]:
        parameter_value = super()._parameter(parameter_key, quote)
        if parameter_key.endswith("field"):
            parameter_value = self._field_ids.get(parameter_value, parameter_value)
        return parameter_value

    async def _get_source_responses(self, *urls: URL) -> Responses:
        fields_url = URL(f"{await super()._api_url()}/rest/api/2/field")
        response = (await super()._get_source_responses(fields_url))[0]
        self._field_ids = dict((field["name"], field["id"]) for field in await response.json())
        return await super()._get_source_responses(*urls)

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        url = URL(str(self._parameter("url")))
        json = await responses[0].json()
        entities = [self._create_entity(issue, url) for issue in json.get("issues", []) if self._include_issue(issue)]
        return SourceMeasurement(value=str(json.get("total", 0)), entities=entities)

    def _create_entity(self, issue: Dict, url: URL) -> Entity:  # pylint: disable=no-self-use
        """Create an entity from a Jira issue."""
        fields = issue["fields"]
        return dict(
            key=issue["id"], summary=fields["summary"], url=f"{url}/browse/{issue['key']}",
            created=fields["created"], updated=fields.get("updated"), status=fields.get("status", {}).get("name"),
            priority=fields.get("priority", {}).get("name"))

    def _include_issue(self, issue: Dict) -> bool:  # pylint: disable=no-self-use,unused-argument
        """Return whether this issue should be counted."""
        return True

    def _fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        return "summary,created,updated,status,priority"


class JiraManualTestExecution(JiraIssues):
    """Collector for the number of manual test cases that have not been executed recently enough."""

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        measurement = await super()._parse_source_responses(responses)
        measurement.value = str(len(measurement.entities))
        return measurement

    def _create_entity(self, issue: Dict, url: URL) -> Entity:
        entity = super()._create_entity(issue, url)
        entity["last_test_date"] = str(self.__last_test_datetime(issue).date())
        entity["desired_test_frequency"] = str(self.__desired_test_execution_frequency(issue))
        return entity

    def _include_issue(self, issue: Dict) -> bool:
        return days_ago(self.__last_test_datetime(issue)) > self.__desired_test_execution_frequency(issue)

    def _fields(self) -> str:
        return super()._fields() + ",comment"

    @staticmethod
    def __last_test_datetime(issue: Dict) -> datetime:
        """Return the datetime of the last test."""
        comment_dates = [comment["updated"] for comment in issue["fields"]["comment"]["comments"]]
        return parse(max(comment_dates)) if comment_dates else datetime.now()

    def __desired_test_execution_frequency(self, issue: Dict) -> int:
        """Return the desired test frequency for this issue."""
        frequency = issue["fields"].get(self._parameter("manual_test_execution_frequency_field"))
        return int(
            round(float(frequency)) if frequency else str(self._parameter("manual_test_execution_frequency_default")))


class JiraFieldSumBase(JiraIssues):
    """Base class for collectors that sum a custom Jira field."""

    field_parameter = "subclass responsibility"
    entity_key = "subclass responsibility"

    async def _parse_source_responses(self, responses: Responses) -> SourceMeasurement:
        measurement = await super()._parse_source_responses(responses)
        measurement.value = str(round(sum(float(entity[self.entity_key]) for entity in measurement.entities)))
        return measurement

    def _create_entity(self, issue: Dict, url: URL) -> Entity:
        entity = super()._create_entity(issue, url)
        entity[self.entity_key] = str(cast(float, self.__value_of_field_to_sum(issue)))
        return entity

    def _include_issue(self, issue: Dict) -> bool:
        return self.__value_of_field_to_sum(issue) is not None

    def _fields(self) -> str:
        return super()._fields() + "," + cast(str, self._parameter(self.field_parameter))

    def __value_of_field_to_sum(self, issue: Dict) -> Optional[float]:
        """Return the value of the issue field that this collectors is to sum."""
        value = issue["fields"].get(self._parameter(self.field_parameter))
        return value if value is None else float(value)


class JiraReadyUserStoryPoints(JiraFieldSumBase):
    """Collector to get ready user story points from Jira."""

    field_parameter = "story_points_field"
    entity_key = "points"


class JiraManualTestDuration(JiraFieldSumBase):
    """Collector to get manual test duration from Jira."""

    field_parameter = "manual_test_duration_field"
    entity_key = "duration"
