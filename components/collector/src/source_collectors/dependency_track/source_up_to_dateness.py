"""Dependency-Track source up-to-dateness collector."""

from collections.abc import Sequence
from datetime import datetime

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.exceptions import CollectorError
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackBase, DependencyTrackProject


class DependencyTrackSourceUpToDateness(DependencyTrackBase, TimePassedCollector):
    """Collector class to measure the up-to-dateness of a BOM upload."""

    async def _api_url(self) -> URL:
        """Extend to add the projects endpoint to the API URL."""
        return URL(await super()._api_url() + "/project")

    async def _parse_source_response_date_times(self, responses: SourceResponses) -> Sequence[datetime]:
        """Override to parse the timestamp from the responses."""
        if datetimes := [
            self._last_bom_import_datetime(project)
            for response in responses
            async for project in self._get_projects_from_response(response)
        ]:
            return datetimes
        error_message = "No projects found"
        raise CollectorError(error_message)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        landing_url = str(self._parameter("landing_url")).strip("/")
        entities = Entities()
        for response in responses:
            async for project in self._get_projects_from_response(response):
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
