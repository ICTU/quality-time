"""GitLab merge requests collector."""

from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import GitLabBase


class GitLabMergeRequests(GitLabBase):
    """Collector class to measure the number of merge requests."""

    async def _api_url(self) -> URL:
        """Override to return the merge requests API."""
        return await self._gitlab_api_url("merge_requests")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{str(await super()._landing_url(responses))}/{self._parameter('project')}/-/merge_requests")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to get the merge requests."""
        entities = [
            Entity(
                key=merge_request["id"],
                title=merge_request["title"],
                url=merge_request["web_url"],
                state=merge_request["state"],
                created=merge_request.get("created_at"),
                updated=merge_request.get("updated_at"),
                merged=merge_request.get("merged_at"),
                closed=merge_request.get("closed_at"),
            )
            for merge_request in await self._merge_requests(responses)
            if self._include_merge_request(merge_request)
        ]
        return SourceMeasurement(entities=entities)

    @staticmethod
    async def _merge_requests(responses: SourceResponses):
        """Return the list of merge requests."""
        merge_requests = await responses[0].json()
        return [merge_request for merge_request in merge_requests]

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        return merge_request["state"] in self._parameter("merge_request_state")
