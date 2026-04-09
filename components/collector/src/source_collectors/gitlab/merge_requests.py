"""GitLab merge requests collector."""

import aiohttp
from aiogqlc import GraphQLClient

from base_collectors import MergeRequestCollector
from collector_utilities.exceptions import CollectorError, NotFoundError
from collector_utilities.type import URL, Value
from model import Entities, Entity, SourceResponses

from .base import GitLabBase

# GraphQL query to retrieve the merge requests for a specific project. The project id is passed as a variable. This
# string needs to be formatted with or without the approved field name, depending on whether the GitLab instance has
# the approved field, and with the pagination arguments, depending on whether the query is used for the first page or
# for consecutive pages.
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
        draft
        {approved}
      }}
    }}
  }}
}}
"""


class GitLabMergeRequestInfoError(NotFoundError):
    """GitLab merge request info is missing."""

    def __init__(self, project: str) -> None:
        tip = (
            "Please check if the project (name with namespace or id) and private token (with read_api scope) are "
            "configured correctly."
        )
        super().__init__("Merge request info for project", project, extra=tip)


class _ApprovedFieldUnknownError(Exception):
    """Raised when GitLab reports the MergeRequest.approved field as unknown."""


class GitLabMergeRequests(MergeRequestCollector, GitLabBase):
    """Collector class to measure the number of merge requests."""

    APPROVED_FIELD = "approved"  # Name of the merge request approved field in the GitLab GraphQL API

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project merge requests landing page."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('project')}/-/merge_requests")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override to use the GitLab GraphQL API to retrieve the merge requests.

        We can't use the GitLab REST API because that API doesn't support the approved field of merge requests.
        Unfortunately, the free version of GitLab also doesn't support the approved field, even when using the GraphQL
        API, so before we query for merge requests, we first have to find out whether the approved field is supported.
        """
        api_url = await self._api_url()
        timeout = aiohttp.ClientTimeout(total=self._session.timeout.total)
        # We need to create a new session because the GraphQLClient expects the session to provide the headers.
        # raise_for_status is False so we can inspect GraphQL error bodies (e.g. HTTP 400 on unknown field).
        async with aiohttp.ClientSession(raise_for_status=False, timeout=timeout, headers=self._headers()) as session:
            client = GraphQLClient(f"{api_url}/api/graphql", session=session)
            approved_field = await self._approved_field(client)
            responses, has_next_page, cursor = SourceResponses(), True, ""
            while has_next_page:
                response, has_next_page, cursor = await self._get_merge_request_response(client, approved_field, cursor)
                responses.append(response)
        return responses

    async def _approved_field(self, client: GraphQLClient) -> str:
        """Determine whether the GitLab instance has the approved field for merge requests.

        This is done by running a dry-run first-page merge-requests query that includes the approved field. If
        GitLab accepts it, the field is supported; if GitLab rejects it as unknown, it isn't. The first page is
        then fetched again by the pagination loop, for a total call count that matches the previous introspection
        approach.
        """
        try:
            await self._get_merge_request_response(client, self.APPROVED_FIELD)
        except _ApprovedFieldUnknownError:
            return ""
        return self.APPROVED_FIELD

    async def _get_merge_request_response(
        self,
        client: GraphQLClient,
        approved_field: str,
        cursor: str = "",
    ) -> tuple[aiohttp.ClientResponse, bool, str]:
        """Return the merge request response, whether there are more pages, and a cursor to the next page, if any."""
        pagination = f'(after: "{cursor}")' if cursor else ""
        merge_request_query = MERGE_REQUEST_QUERY.format(pagination=pagination, approved=approved_field)
        response = await client.execute(merge_request_query, variables={"projectId": self._parameter("project")})
        json = await response.json()
        if errors := json.get("errors"):
            message = errors[0].get("message") or "unknown GitLab error"
            if self.APPROVED_FIELD in message and ("doesn't exist" in message or "Field '" in message):
                raise _ApprovedFieldUnknownError(message)
            response.raise_for_status()  # Surface HTTP errors (e.g. 400) if any.
            raise CollectorError(message)  # Otherwise surface the GraphQL error message.
        response.raise_for_status()
        if project := json["data"]["project"]:
            page_info = project["mergeRequests"]["pageInfo"]
            return response, page_info["hasNextPage"], page_info.get("endCursor", "")
        raise GitLabMergeRequestInfoError(str(self._parameter("project")))

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the merge requests."""
        merge_requests = []
        for response in responses:
            json = await response.json()
            merge_requests.extend(json["data"]["project"]["mergeRequests"]["nodes"])
        return Entities(self._create_entity(mr) for mr in merge_requests)

    async def _parse_total(self, responses: SourceResponses, entities: Entities) -> Value:
        """Override to parse the total number of merge requests."""
        return str((await responses[0].json())["data"]["project"]["mergeRequests"]["count"])

    def _create_entity(self, merge_request) -> Entity:
        """Create an entity from a GitLab JSON merge request."""
        return Entity(
            key=merge_request["id"],
            title=merge_request["title"],
            target_branch=merge_request["targetBranch"],
            url=merge_request["webUrl"],
            state=merge_request["state"],
            approved=self.__approval_state(merge_request),
            created=merge_request["createdAt"],
            updated=merge_request["updatedAt"],
            merged=merge_request["mergedAt"],
            downvotes=str(merge_request["downvotes"]),
            upvotes=str(merge_request["upvotes"]),
            draft=str(merge_request.get("draft", False)),
        )

    def _request_matches_approval(self, entity: Entity) -> bool:
        """Override to return whether the merge request approval matches the configured approval."""
        return entity["approved"] in self._parameter("approval_state")

    @classmethod
    def __approval_state(cls, merge_request) -> str:
        """Return the merge request approval state."""
        return {True: "yes", False: "no", None: "?"}[merge_request.get(cls.APPROVED_FIELD)]

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the merge request should be counted."""
        return super()._include_entity(entity) and self._request_matches_draft_status(entity)

    def _request_matches_draft_status(self, entity: Entity) -> bool:
        """Return whether the merge request draft status matches the configured draft status."""
        ignore_drafts = self._parameter("ignore_draft_merge_requests")
        is_draft = entity["draft"] == "True"
        return not (ignore_drafts == "yes" and is_draft)
