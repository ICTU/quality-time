"""Jira velocity collector."""

from typing import Dict, List
from urllib.parse import parse_qs, urlparse

from typing_extensions import TypedDict

from base_collectors import SourceCollector, SourceCollectorException
from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses


class JiraVelocity(SourceCollector):
    """Collector to get sprint velocity from Jira."""

    Board = TypedDict("Board", {"id": int, "name": str})
    Points = TypedDict("Points", {"text": str, "value": float})
    Sprint = TypedDict("Sprint", {"id": int, "name": str, "goal": str})
    SprintPoints = Dict[str, Points]

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to pass the Greenhopper velocity chart API."""
        board_id = await self.__board_id(urls[0])
        api_url = URL(f"{urls[0]}/rest/greenhopper/1.0/rapid/charts/velocity.json?rapidViewId={board_id}")
        return await super()._get_source_responses(api_url)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the sprint values from the responses."""
        api_url = await self._api_url()
        board_id = parse_qs(urlparse(str(responses.api_url)).query)["rapidViewId"][0]
        entity_url = URL(
            f"{api_url}/secure/RapidBoard.jspa?rapidView={board_id}&view=reporting&chart=sprintRetrospective&sprint="
        )
        json = await responses[0].json()
        # The JSON contains a list with sprints and a dict with the committed and completed points, indexed by sprint id
        sprints, points = json["sprints"], json["velocityStatEntries"]
        velocity_type = str(self._parameter("velocity_type"))
        nr_sprints = int(str(self._parameter("velocity_sprints")))
        # Get the points, either completed, committed, or completed minus committed, as determined by the velocity type
        sprint_values = [self.__velocity(points[str(sprint["id"])], velocity_type) for sprint in sprints[:nr_sprints]]
        entities = [self.__entity(sprint, points[str(sprint["id"])], velocity_type, entity_url) for sprint in sprints]
        return SourceMeasurement(
            value=str(round(sum(sprint_values) / len(sprint_values))) if sprint_values else "0", entities=entities
        )

    @staticmethod
    def __velocity(sprint_points: SprintPoints, velocity_type: str) -> float:
        """Return the points completed, points committed, or difference between the two for the sprint."""
        if velocity_type == "difference":
            return sprint_points["completed"]["value"] - sprint_points["estimated"]["value"]
        return sprint_points[velocity_type]["value"]

    @staticmethod
    def __entity(sprint: Sprint, sprint_points: SprintPoints, velocity_type: str, entity_url: URL) -> Entity:
        """Create a sprint entity."""
        sprint_id = str(sprint["id"])
        committed = sprint_points["estimated"]["text"]
        completed = sprint_points["completed"]["text"]
        difference = str(float(sprint_points["completed"]["value"] - sprint_points["estimated"]["value"]))
        measured = dict(completed=completed, estimated=committed, difference=difference)[velocity_type]
        return Entity(
            key=sprint_id,
            name=sprint["name"],
            goal=sprint.get("goal") or "",
            points_completed=completed,
            points_committed=committed,
            points_measured=measured,
            points_difference=difference,
            url=str(entity_url) + sprint_id,
        )

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to create a link to the Greenhopper velocity chart."""
        api_url = await self._api_url()
        board_id = parse_qs(urlparse(str(responses.api_url)).query)["rapidViewId"][0]
        return URL(f"{api_url}/secure/RapidBoard.jspa?rapidView={board_id}&view=reporting&chart=velocityChart")

    async def __board_id(self, api_url: URL) -> str:
        """Return the board id."""
        last = False
        start_at = 0
        boards: List[JiraVelocity.Board] = []
        while not last:
            url = URL(f"{api_url}/rest/agile/1.0/board?startAt={start_at}")
            response = (await super()._get_source_responses(url))[0]
            json = await response.json()
            boards.extend(json["values"])
            start_at += json["maxResults"]
            last = json["isLast"]
        board_name_or_id = str(self._parameter("board")).lower()
        matching_boards = [b for b in boards if board_name_or_id in (str(b["id"]), b["name"].lower().strip())]
        if not matching_boards:
            message = f"Could not find a Jira board with id or name '{board_name_or_id}' at {api_url}"
            raise SourceCollectorException(message)
        return str(matching_boards[0]["id"])
