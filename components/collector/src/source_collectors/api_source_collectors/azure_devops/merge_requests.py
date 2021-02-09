"""Azure Devops Server merge requests collector."""

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
        entities = [
            Entity(
                key=merge_request["pullRequestId"],
                title=merge_request["title"],
                target_branch=merge_request["targetRefName"],
                url=merge_request["url"],
                state=merge_request["status"],
                created=merge_request.get("creationDate"),
                closed=merge_request.get("closedDate"),
                downvotes=str(len([r for r in merge_request.get("reviewers", []) if r["vote"] < 0])),
                upvotes=str(len([r for r in merge_request.get("reviewers", []) if r["vote"] > 0])),
            )
            for merge_request in merge_requests
            if self._include_merge_request(merge_request)
        ]
        return SourceMeasurement(entities=entities, total=str(len(merge_requests)))

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        return True
