"""GitLab CI-pipelines collector."""

from typing import TYPE_CHECKING

from collector_utilities.date_time import parse_datetime
from model import Entities

from .base import GitLabPipelineBase

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import URL
    from model import Entity, SourceResponses


class GitLabPipelines(GitLabPipelineBase):
    """Collector class to count GitLab CI-pipelines."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Extend to optionally keep only the most recent pipeline per branch.

        The most recent pipeline per branch is selected before the pipeline status filter is applied (the status
        filter is applied by GitLabPipelineBase._include_entity()) so that the metric can report whether the most
        recent pipeline of a branch has a certain status.
        """
        entities = await super()._parse_entities(responses)
        if self._parameter("only_include_most_recent_pipeline_per_branch") == "yes":
            entities = self.__most_recent_entity_per_branch(entities)
        return entities

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return the pipelines page of the project, because the metric may measure zero pipelines."""
        return await self._project_pipelines_landing_url(responses)

    def __most_recent_entity_per_branch(self, entities: Entities) -> Entities:
        """Return the most recent pipeline of each branch, ignoring pipelines that don't match the other filters."""
        most_recent: dict[str, Entity] = {}
        for entity in entities:
            if not self._matches_selection_filters(entity):
                continue
            current = most_recent.get(entity["ref"])
            if current is None or self.__sort_key(entity) > self.__sort_key(current):
                most_recent[entity["ref"]] = entity
        return Entities(most_recent.values())

    @staticmethod
    def __sort_key(entity: Entity) -> tuple[datetime, int]:
        """Return the sort key of the entity: its date and time, with the pipeline id as tie breaker."""
        return parse_datetime(entity["updated"] or entity["created"]), int(entity["key"])
