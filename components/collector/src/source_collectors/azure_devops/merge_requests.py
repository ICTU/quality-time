"""Azure Devops Server merge requests collector."""

from typing import cast

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Value
from source_model import Entities, Entity, SourceResponses

from .base import AzureDevopsRepositoryBase


class AzureDevopsMergeRequests(AzureDevopsRepositoryBase):
    """Collector for merge requests (pull requests in Azure Devops)."""

    PAGE_SIZE = 100  # Page size for Azure Devops pagination

    async def _api_url(self) -> URL:
        """Extend to add the pull requests API path."""
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/pullrequests?api-version=4.1&searchCriteria.status=all&$top={self.PAGE_SIZE}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the pull requests path."""
        landing_url = str(await super()._landing_url(responses))
        return URL(f"{landing_url}/pullrequests")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to use Azure Devops pagination, if necessary."""
        nr_merge_requests_to_skip = 0
        responses = await super()._get_source_responses(*urls)
        while len((await responses[-1].json())["value"]) == self.PAGE_SIZE:
            nr_merge_requests_to_skip += self.PAGE_SIZE
            responses.extend(await super()._get_source_responses(URL(f"{urls[0]}&$skip={nr_merge_requests_to_skip}")))
        return responses

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the merge requests from the responses."""
        merge_requests = []
        for response in responses:
            merge_requests.extend((await response.json())["value"])
        landing_url = (await self._landing_url(responses)).rstrip("s")
        return [self._create_entity(mr, landing_url) for mr in merge_requests if self._include_merge_request(mr)]

    async def _parse_total(self, responses: SourceResponses) -> Value:
        """Override to parse the total number of merge requests from the responses."""
        return str(sum([len((await response.json())["value"]) for response in responses]))

    def _create_entity(self, merge_request, landing_url: str) -> Entity:
        """Create an entity from a Azure Devops JSON result."""
        return Entity(
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

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        request_matches_state = merge_request["status"] in self._parameter("merge_request_state")
        branches = self._parameter("target_branches_to_include")
        target_branch = merge_request["targetRefName"]
        request_matches_branches = match_string_or_regular_expression(target_branch, branches) if branches else True
        # If the required number of upvotes is zero, merge requests are included regardless of how many upvotes they
        # actually have. If the required number of upvotes is more than zero then only merge requests that have fewer
        # than the minimum number of upvotes are included in the count:
        required_upvotes = int(cast(str, self._parameter("upvotes")))
        request_has_fewer_than_min_upvotes = required_upvotes == 0 or self._upvotes(merge_request) < required_upvotes
        return request_matches_state and request_matches_branches and request_has_fewer_than_min_upvotes

    @staticmethod
    def _downvotes(merge_request) -> int:
        """Return the number of downvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("vote", 0) < 0])

    @staticmethod
    def _upvotes(merge_request) -> int:
        """Return the number of upvotes the merge request has."""
        return len([r for r in merge_request.get("reviewers", []) if r.get("vote", 0) > 0])
