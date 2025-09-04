"""Dependency-Track source up-to-dateness collector."""

from collections.abc import Sequence
from datetime import datetime
from typing import Literal

from shared_data_model import DATA_MODEL

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_from_timestamp
from collector_utilities.exceptions import CollectorError
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses

from .base import DependencyTrackBase
from .json_types import DependencyTrackProject


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
                    project_version=project.get("version", ""),
                    is_latest="true" if self._is_latest(project) else "false",
                    up_to_date=self._up_to_dateness(project),
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

    def _up_to_dateness(self, project: DependencyTrackProject) -> str:
        """Return the up-to-dateness of the project."""
        date_times = self._project_event_datetimes(project)
        if not date_times:
            return "unknown"
        # Use the minimum of the project's last BOM-import and last BOM-analysis dates as the project's up-to-dateness:
        min_date_time = self.days(self.minimum(date_times))
        if self._target_met(min_date_time, "target"):
            return "yes"
        if self._target_met(min_date_time, "near_target"):
            return "nearly"
        return "no"

    def _target_met(self, value: int, target_type: Literal["target", "near_target"]) -> bool:
        """Return whether the value meets the target value."""
        target = int(self._metric.get(target_type) or getattr(DATA_MODEL.metrics[self._metric["type"]], target_type))
        # In practice, the direction of the metric should always be "<" (smaller is better), but the user can change
        # the direction, so better be prepared:
        return value <= target if self.metric_direction == "<" else value >= target
