"""Bitbucket collector base classes."""

from abc import ABC

from base_collectors import SourceCollector
from collector_utilities.functions import add_query
from collector_utilities.type import URL
from model import SourceResponses


class BitbucketBase(SourceCollector, ABC):
    """Base class for Bitbucket collectors."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to follow Bitbucket pagination links, if necessary."""
        all_responses = responses = await super()._get_source_responses(*urls)
        while next_urls := await self._next_urls(responses):
            # Retrieving consecutive big responses without reading the response hangs the client, see
            # https://github.com/aio-libs/aiohttp/issues/2217
            for response in responses:
                await response.read()
            all_responses.extend(responses := await super()._get_source_responses(*next_urls))
        return all_responses

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Authorization"] = "Bearer " + str(private_token)
        return headers

    async def _next_urls(self, responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses."""
        return [URL(next_url) for response in responses if (next_url := response.links.get("next", {}).get("url"))]


class BitbucketProjectBase(BitbucketBase, ABC):
    """Base class for Bitbucket collectors for a specific project."""

    async def _bitbucket_api_url(self, api: str) -> URL:
        """Return a Bitbucket API url for a project, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project")
        api_url = URL(f"{url}/rest/api/1.0/projects/{project}" + (f"/{api}" if api else ""))
        return add_query(api_url, "pagelen=100")