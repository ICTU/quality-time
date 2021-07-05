"""GitLab merge requests collector."""

from typing import cast

import aiohttp
from aiogqlc import GraphQLClient

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Value
from source_model import Entities, Entity, SourceResponses

from .base import GitLabProjectBase

MERGE_REQUEST_FIELDS_QUERY = """
{
  __type(name: "MergeRequest") {
    fields {
      name
    }
  }
}
"""

MERGE_REQUEST_QUERY = """
query MRs($projectId: ID!) {{
  project(fullPath: $projectId) {{
    mergeRequests{pagination} {{
      count
      pageInfo {{
        endCursor
        hasNextPage
      }}
      nodes {{
        id
        state
        title
        targetBranch
        webUrl
        upvotes
        downvotes
        createdAt
        updatedAt
        mergedAt
        {approved}
      }}
    }}
  }}
}}
"""


class GitLabMergeRequests(GitLabProjectBase):
    """Collector class to measure the number of merge requests."""

    async def _api_url(self) -> URL:
        """Override to return the merge requests API."""
        return await self._gitlab_api_url("merge_requests")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{str(await super()._landing_url(responses))}/{self._parameter('project')}/-/merge_requests")

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:
        """Override to determine whether the configured GitLab is premium and thus has the 'approved' field."""
        api_url = await super()._api_url()
        timeout = aiohttp.ClientTimeout(total=120)
        # We need to create a new session because the GraphQLClient expects the session to have the headers.
        async with aiohttp.ClientSession(raise_for_status=True, timeout=timeout, headers=self._headers()) as session:
            client = GraphQLClient(f"{api_url}/api/graphql", session=session)
            approved_field = await self._approved_field(client)
            responses, has_next_page, cursor = SourceResponses(), True, ""
            while has_next_page:
                response, has_next_page, cursor = await self._get_merge_request_response(client, approved_field, cursor)
                responses.append(response)
        return responses

    @staticmethod
    async def _approved_field(client: GraphQLClient) -> str:
        """Determine whether the GitLab instance has the approved field for merge requests."""
        response = await client.execute(MERGE_REQUEST_FIELDS_QUERY)
        json = await response.json()
        fields = [field["name"] for field in json["data"]["__type"]["fields"]]
        return "approved" if "approved" in fields else ""

    async def _get_merge_request_response(
        self, client: GraphQLClient, approved_field: str, cursor: str = ""
    ) -> tuple[SourceResponses, bool, str]:
        """Return the merge request response, and a cursor to the next page with merge requests, if available."""
        pagination = f'(after: "{cursor}")' if cursor else ""
        merge_request_query = MERGE_REQUEST_QUERY.format(pagination=pagination, approved=approved_field)
        response = await client.execute(merge_request_query, variables=dict(projectId=self._parameter("project")))
        json = await response.json()
        page_info = json["data"]["project"]["mergeRequests"]["pageInfo"]
        return response, page_info["hasNextPage"], page_info.get("endCursor", "")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the merge requests."""
        merge_requests = []
        for response in responses:
            json = await response.json()
            merge_requests.extend(json["data"]["project"]["mergeRequests"]["nodes"])
        return Entities(self._create_entity(mr) for mr in merge_requests if self._include_merge_request(mr))

    async def _parse_total(self, responses: SourceResponses) -> Value:
        """Override to parse the total number of merge requests."""
        return str((await responses[0].json())["data"]["project"]["mergeRequests"]["count"])

    @staticmethod
    def _create_entity(merge_request) -> Entity:
        """Create an entity from a GitLab JSON result."""
        return Entity(
            key=merge_request["id"],
            title=merge_request["title"],
            target_branch=merge_request["targetBranch"],
            url=merge_request["webUrl"],
            state=merge_request["state"],
            approved={True: "yes", False: "no", None: "?"}[merge_request.get("approved")],
            created=merge_request["createdAt"],
            updated=merge_request["updatedAt"],
            merged=merge_request["mergedAt"],
            downvotes=str(merge_request["downvotes"]),
            upvotes=str(merge_request["upvotes"]),
        )

    def _include_merge_request(self, merge_request) -> bool:
        """Return whether the merge request should be counted."""
        request_matches_state = merge_request["state"] in self._parameter("merge_request_state")
        branches = self._parameter("target_branches_to_include")
        target_branch = merge_request["targetBranch"]
        request_matches_branches = match_string_or_regular_expression(target_branch, branches) if branches else True
        # If the required number of upvotes is zero, merge requests are included regardless of how many upvotes they
        # actually have. If the required number of upvotes is more than zero then only merge requests that have fewer
        # than the minimum number of upvotes are included in the count:
        required_upvotes = int(cast(str, self._parameter("upvotes")))
        request_has_fewer_than_min_upvotes = required_upvotes == 0 or int(merge_request["upvotes"]) < required_upvotes
        return request_matches_state and request_matches_branches and request_has_fewer_than_min_upvotes
