"""GitLab CI-pipeline duration collector."""

from typing import TYPE_CHECKING

from collector_utilities.date_time import minutes
from collector_utilities.exceptions import CollectorError

from .base import GitLabPipelineBase

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, Entity, SourceResponses

    from .json_types import Pipeline


class GitLabPipelineDuration(GitLabPipelineBase):
    """GitLab CI-pipeline duration collector."""

    def _create_entity(self, pipeline: Pipeline) -> Entity:
        """Extend to also add the duration to the entity created from a GitLab pipeline."""
        entity = super()._create_entity(pipeline)
        entity["duration"] = str(minutes(pipeline.bruto_duration))
        return entity

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Extend to replace the bruto durations with the netto durations, if idle time is to be excluded."""
        entities = await super()._parse_entities(responses)
        if self._parameter("exclude_idle_time_from_pipeline_duration") == "yes":
            await self._replace_bruto_with_netto_duration(entities)
        return entities

    async def _replace_bruto_with_netto_duration(self, entities: Entities) -> None:
        """Replace the duration of the entities that pass the filters with the netto duration of their pipeline.

        Only the GitLab API to get one pipeline returns the duration of a pipeline, so the details of each pipeline
        that passes the filters have to be retrieved separately. The key of the entities is the pipeline id.
        """
        included_entities = [entity for entity in entities if self._include_entity(entity)]
        pipelines = await self._pipeline_details([entity["key"] for entity in included_entities])
        for entity, pipeline in zip(included_entities, pipelines, strict=True):
            entity["duration"] = str(minutes(pipeline.netto_duration))

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Parse the value from the responses."""
        if not included_entities:
            error_message = "No pipelines found with given filter(s)"
            raise CollectorError(error_message)
        match self._parameter("pipeline_selection"):
            case "slowest":
                return str(max(self._durations(included_entities)))
            case "latest":
                included_entities.sort(key=lambda entity: entity["updated"] or entity["created"])
                return str(included_entities[-1]["duration"])
            case "average":
                return str(round(sum(self._durations(included_entities)) / len(included_entities)))
            case _:  # pragma: no cover
                error_message = "Invalid value for the pipeline selection parameter"
                raise CollectorError(error_message)

    def _durations(self, entities: Entities) -> list[int]:
        """Return the pipeline durations of the entities."""
        return [int(entity["duration"]) for entity in entities]
