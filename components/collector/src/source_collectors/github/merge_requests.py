"""GitHub merge requests collector."""

import logging
from typing import cast

import aiohttp # type: ignore
from aiogqlc import GraphQLClient # type: ignore

from collector_utilities.exceptions import NotFoundError
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Value
from model import Entities, Entity, SourceResponses

from .base import GitHubBase

# GraphQL query to retrieve the pull requests for a specific repository. The repository name is passed as a variable.
# This string needs to be formatted with the pagination arguments, depending on whether the query is used for the
# first page or for consecutive pages.

PULL_REQUEST_QUERY = """
query ($repository: String!, $owner: String!) {{
  repository(owner: $owner, name: $repository) {{
    pullRequests{pagination} {{
      totalCount
      pageInfo {{
        endCursor
        hasNextPage
      }}
      nodes {{
        id
        state
        title
        baseRefName
        url
        createdAt
        updatedAt
        mergedAt
        reviewDecision
        reactions(content: THUMBS_UP) {{
          totalCount
        }}
        comments {{
          totalCount
        }}
      }}
    }}
  }}
}}
"""

class GitHubPullRequestInfoError(NotFoundError):
    """GitHub pull request info is missing."""

    def __init__(self, owner: str, repository: str) -> None:
        tip = (
          "Please check if the repository (name with owner) and access token (with repo scope) are "
          "configured correctly."
        )
        super().__init__("Pull request info for repository", owner, repository, extra=tip)
        
class GitHubMergeRequests(GitHubBase):
    """Collector class to measure the number of pull requests."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the repository pull requests."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('owner')}/{self._parameter('repository')}/pulls")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override to use the GitHub GraphQL API to retrieve the pull requests."""
        api_url = await self._api_url()
        timeout = aiohttp.ClientTimeout(total=self._session.timeout.total)
        # We need to create a new session because the GraphQLClient expects the session to provide the headers:
        async with aiohttp.ClientSession(raise_for_status=True, timeout=timeout, headers=self._headers()) as session:
            client = GraphQLClient(f"{api_url}/graphql", session=session)
            responses, has_next_page, cursor = SourceResponses(), True, ""
            while has_next_page:
                response, has_next_page, cursor = await self._get_pull_request_response(client, cursor)
                responses.append(response)
        return responses

    async def _get_pull_request_response(
        self,
        client: GraphQLClient,
        cursor: str = "",
    ) -> tuple[aiohttp.ClientResponse, bool, str]:
        """Return the pull request response, whether there are more pages, and a cursor to the next page, if any."""
        pagination = f'(first: 100, after: "{cursor}")'
        pull_request_query = PULL_REQUEST_QUERY.format(pagination=pagination)
        logging.error(pull_request_query);
        response = await client.execute(pull_request_query, variables={"repository": self._parameter("repository"), "owner": self._parameter("owner")})
        json = await response.json()
        if repository := json["data"]["repository"]:
            page_info = repository["pullRequests"]["pageInfo"]
            return response, page_info["hasNextPage"], page_info.get("endCursor", "")
        raise GitHubPullRequestInfoError(f"{self._parameter('owner')}/{self._parameter('repository')}")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the pull requests."""
        pull_requests = []
        for response in responses:
            json = await response.json()
            pull_requests.extend(json["data"]["repository"]["pullRequests"]["nodes"])
        return Entities(self._create_entity(pr) for pr in pull_requests)

    async def _parse_total(self, responses: SourceResponses) -> Value:
        """Override to parse the total number of pull requests."""
        return str((await responses[0].json())["data"]["repository"]["pullRequests"]["totalCount"])

    def _create_entity(self, pull_request) -> Entity:
        """Create an entity from a GitHub JSON pull request."""
        return Entity(
            key=pull_request["id"],
            title=pull_request["title"],
            base_ref_name=pull_request["baseRefName"],
            url=pull_request["url"],
            state=pull_request["state"],
            review_decision=pull_request["reviewDecision"],
            created=pull_request["createdAt"],
            updated=pull_request["updatedAt"],
            merged=pull_request["mergedAt"],
            comments=str(pull_request["comments"]["totalCount"]),
            thumbs_up=str(pull_request["reactions"]["totalCount"]),
        )

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the pull request should be counted."""
        pr_matches_state = entity["state"] in self._parameter("merge_request_state")
        # pr_matches_review_decision = entity["review_decision"] in self._parameter("review_decision")
        # base_ref_name = entity["base_ref_name"]
        # branches = self._parameter("base_refs_to_include")
        # pr_matches_branches = match_string_or_regular_expression(base_ref_name, branches) if branches else True
        
        
        # If the required number of thumbs up is zero, pull requests are included regardless of how many thumbs up they
        # actually have. If the required number of thumbs up is more than zero then only pull requests that have fewer
        # than the minimum number of thumbs up are included in the count:
        
        # and pr_matches_review_decision and pr_matches_branches
        return pr_matches_state 