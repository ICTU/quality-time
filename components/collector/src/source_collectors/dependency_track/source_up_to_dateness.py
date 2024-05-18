"""Dependency-Track source up-to-dateness collector."""

from datetime import datetime
from typing import TypedDict

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.type import URL, Response
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackBase


class DependencyTrackProject(TypedDict):
    """Project as returned by Dependency-Track."""

    lastBomImport: int  # Timestamp
    name: str
    uuid: str


class DependencyTrackSourceUpToDateness(DependencyTrackBase, TimePassedCollector):
    """Collector class to measure the up-to-dateness of a BOM upload."""

    async def _api_url(self) -> URL:
        """Extend to add the projects endpoint to the API URL."""
        return URL(await super()._api_url() + "/project")

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the timestamp from the response."""
        projects = await response.json(content_type=None)
        datetimes = [self._last_bom_import_datetime(project) for project in projects]
        return self.minimum(datetimes)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        landing_url = str(self._parameter("landing_url")).strip("/")
        entities = Entities()
        for response in responses:
            for project in await response.json(content_type=None):
                uuid = project["uuid"]
                entity = Entity(
                    key=uuid,
                    last_bom_import=self._last_bom_import_datetime(project).isoformat(),
                    project=project["name"],
                    project_landing_url=f"{landing_url}/projects/{uuid}",
                )
                entities.append(entity)
        return entities

    @staticmethod
    def _last_bom_import_datetime(project: DependencyTrackProject) -> datetime:
        """Return the last BOM import datetime for the project."""
        return datetime_from_timestamp(int(project["lastBomImport"]))
