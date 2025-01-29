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
            return str(max(durations))
        error_message = "No pipelines found within the lookback period"
        raise CollectorError(error_message)
