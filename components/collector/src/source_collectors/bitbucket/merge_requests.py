"""Bitbucket merge requests collector."""

from typing import TYPE_CHECKING

from base_collectors import MergeRequestCollector
from model import Entities, Entity, SourceResponses

from .base import BitbucketProjectBase

if TYPE_CHECKING:
    from collector_utilities.type import URL


class BitbucketMergeRequests(MergeRequestCollector, BitbucketProjectBase):
    """Collector for merge requests in Bitbucket."""

    async def _api_url(self) -> URL:
        """Override to return the merge requests API."""
        return await self._bitbucket_api_url("pull-requests")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project merge requests."""
        return await self._bitbucket_landing_url(responses, "pull-requests")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the entities from the responses."""
        merge_requests = []
        for response in responses:
            merge_requests.extend((await response.json())["values"])
        landing_url = await self._landing_url(responses)
        return Entities([self._create_entity(mr, landing_url) for mr in merge_requests])

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

    @staticmethod
    def _downvotes(merge_request) -> int:
        """Return the number of downvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if not r.get("approved", False)])

    @staticmethod
    def _upvotes(merge_request) -> int:
        """Return the number of upvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("approved", False)])
