"""Bitbucket collector base classes."""

from abc import ABC

from base_collectors import SourceCollector
from collector_utilities.functions import add_query
from collector_utilities.type import URL, Value
from model import Entities, SourceResponses


class BitbucketBase(SourceCollector, ABC):
    """Base class for Bitbucket collectors."""

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Authorization"] = "Bearer " + str(private_token)
        return headers

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to use Bitbucket pagination, if necessary."""
        responses = SourceResponses()
        isLastPage = False
        nr_merge_requests_to_skip = 0
        while not isLastPage:
            responses.extend(await super()._get_source_responses(URL(f"{urls[0]}&start={nr_merge_requests_to_skip}")))
            json = await responses[-1].json()
            nr_merge_requests_to_skip = json.get("nextPageStart", 0)
            isLastPage = json["isLastPage"]
        return responses

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the entities from the responses."""
        merge_requests = []
        for response in responses:
            merge_requests.extend((await response.json())["values"])
        landing_url = (await self._landing_url(responses))
        return Entities([self._create_entity(mr, landing_url) for mr in merge_requests])

    async def _parse_total(self, responses: SourceResponses) -> Value:
        """Override to parse the total number of entities from the responses."""
        merge_requests = [(await response.json())["size"] for response in responses]
        return str(sum(merge_requests))


class BitbucketProjectBase(BitbucketBase, ABC):
    """Base class for Bitbucket collectors for a specific project."""

    async def _bitbucket_api_url(self, api: str, page_size: int) -> URL:
        """Return a Bitbucket API url for a project, if present in the parameters."""
        url = await super()._api_url()
        project = f"{self._parameter('owner')}/repos/{self._parameter('repository')}"
        api_url = URL(f"{url}/rest/api/1.0/projects/{project}" + (f"/{api}?limit{page_size}" if api else ""))
        return add_query(api_url, "&details=true")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project merge requests."""
        project = f"projects/{self._parameter('owner')}/repos/{self._parameter('repository')}"
        return URL(f"{await super()._landing_url(responses)}/{project}/pull-requests")
