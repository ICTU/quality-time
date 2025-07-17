"""GitLab CI-pipeline duration collector."""

from typing import TYPE_CHECKING

from collector_utilities.exceptions import CollectorError

from .base import GitLabPipelineBase

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, SourceResponses


class GitLabPipelineDuration(GitLabPipelineBase):
    """GitLab CI-pipeline duration collector."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Parse the value from the responses."""
        if not included_entities:
            error_message = "No pipelines found within the lookback period"
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
