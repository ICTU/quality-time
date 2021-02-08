"""GitLab merge requests collector."""

from typing import cast

from collector_utilities.functions import match_string_or_regular_expression
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
        merge_requests = await self._merge_requests(responses)
        entities = [
            Entity(
                key=merge_request["id"],
                title=merge_request["title"],
                target_branch=merge_request["target_branch"],
                url=merge_request["web_url"],
                state=merge_request["state"],
                created=merge_request.get("created_at"),
                updated=merge_request.get("updated_at"),
                merged=merge_request.get("merged_at"),
                closed=merge_request.get("closed_at"),
                downvotes=str(merge_request.get("downvotes", 0)),
                upvotes=str(merge_request.get("upvotes", 0)),
            )
            for merge_request in merge_requests
            if self._include_merge_request(merge_request)
        ]
        return SourceMeasurement(entities=entities, total=str(len(merge_requests)))

    @staticmethod
    async def _merge_requests(responses: SourceResponses):
        """Return the list of merge requests."""
        merge_requests = await responses[0].json()
        return [merge_request for merge_request in merge_requests]

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        request_has_fewer_than_min_upvotes = int(merge_request["upvotes"]) < int(cast(str, self._parameter("upvotes")))
        request_matches_state = merge_request["state"] in self._parameter("merge_request_state")
        branches = self._parameter("target_branches_to_include")
        target_branch = merge_request["target_branch"]
        request_matches_branches = branches and match_string_or_regular_expression(target_branch, branches)
        return request_has_fewer_than_min_upvotes and request_matches_state and request_matches_branches
