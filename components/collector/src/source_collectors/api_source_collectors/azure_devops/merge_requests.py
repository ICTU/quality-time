"""Azure Devops Server merge requests collector."""

from typing import cast

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import AzureDevopsRepositoryBase


class AzureDevopsMergeRequests(AzureDevopsRepositoryBase):
    """Collector for merge requests (pull requests in Azure Devops)."""

    async def _api_url(self) -> URL:
        """Extend to add the pull requests API path."""
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/pullrequests?api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the pull requests path."""
        landing_url = str(await super()._landing_url(responses))
        return URL(f"{landing_url}/pullrequests")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the merge requests from the responses."""
        merge_requests = []
        for response in responses:
            merge_requests.extend((await response.json())["value"])
        landing_url = (await self._landing_url(responses)).rstrip("s")
        entities = [
            Entity(
                key=merge_request["pullRequestId"],
                title=merge_request["title"],
                target_branch=merge_request["targetRefName"],
                url=f"{landing_url}/{merge_request['pullRequestId']}",
                state=merge_request["status"],
                created=merge_request.get("creationDate"),
                closed=merge_request.get("closedDate"),
                downvotes=str(self._downvotes(merge_request)),
                upvotes=str(self._upvotes(merge_request)),
            )
            for merge_request in merge_requests
            if self._include_merge_request(merge_request)
        ]
        return SourceMeasurement(entities=entities, total=str(len(merge_requests)))

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        min_upvotes = int(cast(str, self._parameter("upvotes")))
        request_has_fewer_than_min_upvotes = min_upvotes == 0 or self._upvotes(merge_request) < min_upvotes
        request_matches_state = merge_request["status"] in self._parameter("merge_request_state")
        branches = self._parameter("target_branches_to_include")
        target_branch = merge_request["targetRefName"]
        request_matches_branches = match_string_or_regular_expression(target_branch, branches) if branches else True
        return request_has_fewer_than_min_upvotes and request_matches_state and request_matches_branches

    @staticmethod
    def _downvotes(merge_request) -> int:
        """Return the number of downvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("vote", 0) < 0])

    @staticmethod
    def _upvotes(merge_request) -> int:
        """Return the number of upvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("vote", 0) > 0])
