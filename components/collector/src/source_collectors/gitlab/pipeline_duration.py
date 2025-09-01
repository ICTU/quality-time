"""GitLab CI-pipeline duration collector."""

from collector_utilities.exceptions import CollectorError
from collector_utilities.type import Value
from model import Entities, SourceResponses

from .base import GitLabPipelineBase


class GitLabPipelineDuration(GitLabPipelineBase):
    """GitLab CI-pipeline duration collector."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Parse the value from the responses."""
        if durations := [int(entity["duration"]) for entity in included_entities]:
            if self._parameter("pipeline_selection") == "slowest":
                return str(max(durations))
            included_entities.sort(key=lambda entity: entity["updated"] or entity["created"])
            return str(included_entities[-1]["duration"])
        error_message = "No pipelines found within the lookback period"
        raise CollectorError(error_message)
