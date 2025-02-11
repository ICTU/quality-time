"""Bitbucket merge requests collector."""
import pdb
from typing import cast

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Value
from model import Entities, Entity, SourceResponses

from .base import BitbucketProjectBase

class BitbucketMergeRequests(BitbucketProjectBase):
    """Collector for merge requests in Bitbucket."""

    PAGE_SIZE = 100  # Page size for Bitbucket pagination

    async def _api_url(self) -> URL:
        """Override to return the merge requests API."""
        return await self._bitbucket_api_url("pull-requests", self.PAGE_SIZE)

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project merge requests."""
        project = f"projects/{self._parameter('owner')}/repos/{self._parameter('repository')}"
        return URL(f"{await super()._landing_url(responses)}/{project}/pull-requests")

    def _create_entity(self, merge_request, landing_url: str) -> Entity:
        """Create an entity from a Bitbucket JSON result."""
        return Entity(
            key=merge_request["id"],
            title=merge_request["title"],
            target_branch=merge_request["toRef"]["id"],
            url=f"{landing_url}/{merge_request['id']}",
            state=merge_request["state"],
            created=merge_request.get("createdDate"),
            closed=merge_request.get("closedDate"),
            downvotes=str(self._downvotes(merge_request)),
            upvotes=str(self._upvotes(merge_request)),
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the merge request should be counted."""
        request_matches_state = entity["state"] in self._parameter("merge_request_state")
        branches = self._parameter("target_branches_to_include")
        target_branch = entity["target_branch"]
        request_matches_branches = match_string_or_regular_expression(target_branch, branches) if branches else True
        # If the required number of upvotes is zero, merge requests are included regardless of how many upvotes they
        # actually have. If the required number of upvotes is more than zero then only merge requests that have fewer
        # than the minimum number of upvotes are included in the count:
        required_upvotes = int(cast(str, self._parameter("upvotes")))
        request_has_fewer_than_min_upvotes = required_upvotes == 0 or int(entity["upvotes"]) < required_upvotes
        return request_matches_state and request_matches_branches and request_has_fewer_than_min_upvotes

    @staticmethod
    def _downvotes(merge_request) -> int:
        """Return the number of downvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("approved") is False])

    @staticmethod
    def _upvotes(merge_request) -> int:
        """Return the number of upvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("approved") is True])
