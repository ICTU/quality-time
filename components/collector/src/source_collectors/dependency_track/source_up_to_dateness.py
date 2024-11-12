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
        datetimes = []
        for response in responses:
            async for project in self._get_projects_from_response(response):
                datetimes.extend(self._project_event_datetimes(project))
        if datetimes:
            return datetimes
        error_message = "No projects found"
        raise CollectorError(error_message)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        landing_url = str(self._parameter("landing_url")).strip("/")
        entities = Entities()
        for response in responses:
            async for project in self._get_projects_from_response(response):
                last_bom_analysis = self._last_bom_analysis_datetime(project)
                last_bom_import = self._last_bom_import_datetime(project)
                uuid = project["uuid"]
                entity = Entity(
                    key=uuid,
                    last_bom_analysis="" if last_bom_analysis is None else last_bom_analysis.isoformat(),
                    last_bom_import="" if last_bom_import is None else last_bom_import.isoformat(),
                    project=project["name"],
                    project_landing_url=f"{landing_url}/projects/{uuid}",
                )
                entities.append(entity)
        return entities

    def _project_event_datetimes(self, project: DependencyTrackProject) -> list[datetime]:
        """Return the project event (BOM import, BOM analysis) datetimes."""
        datetimes = []
        event_types = self._parameter("project_event_types")
        if "last BOM import" in event_types and (datetime := self._last_bom_import_datetime(project)):
            datetimes.append(datetime)
        if "last BOM analysis" in event_types and (datetime := self._last_bom_analysis_datetime(project)):
            datetimes.append(datetime)
        return datetimes

    @classmethod
    def _last_bom_import_datetime(cls, project: DependencyTrackProject) -> datetime | None:
        """Return the last BOM import datetime for the project."""
        return cls._timestamp_to_datetime(project.get("lastBomImport"))

    @classmethod
    def _last_bom_analysis_datetime(cls, project: DependencyTrackProject) -> datetime | None:
        """Return the last BOM analysis datetime for the project."""
        return cls._timestamp_to_datetime(project.get("metrics", {}).get("lastOccurrence"))

    @staticmethod
    def _timestamp_to_datetime(timestamp: int | None) -> datetime | None:
        """Convert the timestamp to a datetime."""
        return None if timestamp is None else datetime_from_timestamp(timestamp)
