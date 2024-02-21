"""GitLab CI-pipeline duration collector."""

from datetime import timedelta

from collector_utilities.date_time import minutes
from collector_utilities.type import URL, Value
from model import SourceResponses

from .base import GitLabPipelineBase


class GitLabPipelineDuration(GitLabPipelineBase):
    """GitLab CI-pipeline duration collector."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override to get the pipeline details."""
        responses = await super()._get_source_responses(*urls)
        pipelines = await self._pipelines(responses)
        api_url = await self._gitlab_api_url(f"pipelines/{pipelines[0].id}")
        return await super()._get_source_responses(api_url)

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Parse the value from the responses."""
        durations = [pipeline.pipeline_duration for pipeline in await self._pipelines(responses)]
        return str(minutes(max(durations, default=timedelta())))
