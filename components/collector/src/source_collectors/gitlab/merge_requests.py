"""GitLab merge requests collector."""

from typing import cast

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Value
from source_model import Entities, Entity, SourceResponses

from .base import GitLabProjectBase


class GitLabMergeRequests(GitLabProjectBase):
    """Collector class to measure the number of merge requests."""

    async def _api_url(self) -> URL:
        """Override to return the merge requests API."""
        return await self._gitlab_api_url("merge_requests")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{str(await super()._landing_url(responses))}/{self._parameter('project')}/-/merge_requests")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the merge requests."""
        merge_requests = []
        for response in responses:
            merge_requests.extend(await response.json())
        return Entities(self._create_entity(mr) for mr in merge_requests if self._include_merge_request(mr))

    async def _parse_total(self, responses: SourceResponses) -> Value:
        """Override to parse the total number of merge requests."""
        return str(sum([len(await response.json()) for response in responses]))

    @staticmethod
    def _create_entity(merge_request) -> Entity:
        """Create an entity from a GitLab JSON result."""
        return Entity(
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

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        request_matches_state = merge_request["state"] in self._parameter("merge_request_state")
        branches = self._parameter("target_branches_to_include")
        target_branch = merge_request["target_branch"]
        request_matches_branches = match_string_or_regular_expression(target_branch, branches) if branches else True
        # If the required number of upvotes is zero, merge requests are included regardless of how many upvotes they
        # actually have. If the required number of upvotes is more than zero then only merge requests that have fewer
        # than the minimum number of upvotes are included in the count:
        required_upvotes = int(cast(str, self._parameter("upvotes")))
        request_has_fewer_than_min_upvotes = required_upvotes == 0 or int(merge_request["upvotes"]) < required_upvotes
        return request_matches_state and request_matches_branches and request_has_fewer_than_min_upvotes
