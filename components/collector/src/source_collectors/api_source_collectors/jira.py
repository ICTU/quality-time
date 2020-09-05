"""Jira metric collector."""

import re
from datetime import datetime
from typing import Dict, List, Optional, Union, cast
from urllib.parse import parse_qs, urlparse

from dateutil.parser import parse

from base_collectors import SourceCollector
from collector_utilities.functions import days_ago
from collector_utilities.type import URL, Value
from source_model import Entity, SourceMeasurement, SourceResponses


class JiraException(Exception):
    """Something went wrong collecting information from Jira."""


class JiraIssues(SourceCollector):
    """Jira collector for issues."""

    SPRINT_NAME_RE = re.compile(r",name=(.*),startDate=")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field_ids = {}

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        fields_url = URL(f"{url}/rest/api/2/field")
        response = (await super()._get_source_responses(fields_url))[0]
        self._field_ids = {field["name"].lower(): field["id"] for field in await response.json()}
        jql = str(self._parameter("jql", quote=True))
        fields = self._fields()
        return URL(f"{url}/rest/api/2/search?jql={jql}&fields={fields}&maxResults=500")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        jql = str(self._parameter("jql", quote=True))
        return URL(f"{url}/issues/?jql={jql}")

    def _parameter(self, parameter_key: str, quote: bool = False) -> Union[str, List[str]]:
        parameter_value = super()._parameter(parameter_key, quote)
        if parameter_key.endswith("field"):
            parameter_value = self._field_ids.get(str(parameter_value).lower(), parameter_value)
        return parameter_value

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        url = URL(str(self._parameter("url")))
        json = await responses[0].json()
        entities = [self._create_entity(issue, url) for issue in json.get("issues", []) if self._include_issue(issue)]
        return SourceMeasurement(value=self._compute_value(entities), entities=entities)

    @classmethod
    def _compute_value(cls, entities: List[Entity]) -> Value:  # pylint: disable=unused-argument
        """Allow subclasses to compute the value from the entities."""
        return None

    def _create_entity(self, issue: Dict, url: URL) -> Entity:  # pylint: disable=no-self-use
        """Create an entity from a Jira issue."""
        fields = issue["fields"]
        entity_attributes = dict(
            summary=fields["summary"], url=f"{url}/browse/{issue['key']}", created=fields["created"],
            updated=fields.get("updated"), status=fields.get("status", {}).get("name"),
            priority=fields.get("priority", {}).get("name"))
        if sprint_field_id := self._field_ids.get("sprint"):
            entity_attributes["sprint"] = self.__get_sprint_names(fields.get(sprint_field_id) or [])
        return Entity(key=issue["id"], **entity_attributes)

    def _include_issue(self, issue: Dict) -> bool:  # pylint: disable=no-self-use,unused-argument
        """Return whether this issue should be counted."""
        return True

    def _fields(self) -> str:  # pylint: disable=no-self-use
        """Return the fields to get from Jira."""
        sprint_field_id = self._field_ids.get("sprint")
        return "summary,created,updated,status,priority" + (f",{sprint_field_id}" if sprint_field_id else "")

    @classmethod
    def __get_sprint_names(cls, sprint_texts: List[str]) -> str:
        """Parse the sprint name from the sprint text."""
        matches = [cls.SPRINT_NAME_RE.search(sprint_text) for sprint_text in sprint_texts]
        sprint_names = [match.group(1) for match in matches if match]
        return ", ".join(sorted(sprint_names))


class JiraManualTestExecution(JiraIssues):
    """Collector for the number of manual test cases that have not been executed recently enough."""

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

    @classmethod
    def _compute_value(cls, entities: List[Entity]) -> Value:
        # Sum the field, as specified by the entity key, from the entities.
        return str(round(sum(float(entity[cls.entity_key]) for entity in entities)))

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


class JiraUserStoryPoints(JiraFieldSumBase):
    """Collector to get user story points from Jira."""

    field_parameter = "story_points_field"
    entity_key = "points"


class JiraManualTestDuration(JiraFieldSumBase):
    """Collector to get manual test duration from Jira."""

    field_parameter = "manual_test_duration_field"
    entity_key = "duration"


class JiraVelocity(SourceCollector):
    """Collector to get sprint velocity from Jira."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        board_id = await self.__board_id(urls[0])
        api_url = URL(f"{urls[0]}/rest/greenhopper/1.0/rapid/charts/velocity.json?rapidViewId={board_id}")
        return await super()._get_source_responses(api_url)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        api_url = await self._api_url()
        board_id = parse_qs(urlparse(str(responses.api_url)).query)["rapidViewId"][0]
        json = await responses[0].json()
        entities = []
        velocity = []
        points = json["velocityStatEntries"]
        for sprint in json["sprints"]:
            sprint_points = points[str(sprint["id"])]
            velocity.append(sprint_points["completed"]["value"])
            committed = sprint_points["estimated"]["text"]
            completed = sprint_points["completed"]["text"]
            entities.append(
                Entity(
                    key=sprint["id"], name=sprint["name"], goal=sprint.get("goal") or "", points_completed=completed,
                    points_committed=committed,
                    url=f"{api_url}/secure/RapidBoard.jspa?rapidView={board_id}&view=reporting&"
                        f"chart=sprintRetrospective&sprint={sprint['id']}"))
        velocity = velocity[:int(str(self._parameter("velocity_sprints")))]
        return SourceMeasurement(value=str(round(sum(velocity)/len(velocity))) if velocity else "0", entities=entities)

    async def _landing_url(self, responses: SourceResponses) -> URL:
        api_url = await self._api_url()
        board_id = parse_qs(urlparse(str(responses.api_url)).query)["rapidViewId"][0]
        return URL(f"{api_url}/secure/RapidBoard.jspa?rapidView={board_id}&view=reporting&chart=velocityChart")

    async def __board_id(self, api_url: URL) -> str:
        """Return the board id."""
        boards_url = URL(f"{api_url}/rest/agile/1.0/board")
        response = (await super()._get_source_responses(boards_url))[0]
        board_name_or_id = str(self._parameter("board")).lower()
        boards = (await response.json())["values"]
        matching_boards = [
            board for board in boards if board_name_or_id in (str(board["id"]), board["name"].lower().strip())]
        try:
            return str(matching_boards[0]["id"])
        except IndexError as error:
            raise JiraException(
                f"Could not find a Jira board with id or name '{board_name_or_id}' at {api_url}") from error
