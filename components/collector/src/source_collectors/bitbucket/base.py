"""Bitbucket collector base classes."""

from abc import ABC

from base_collectors import SourceCollector
from collector_utilities.functions import add_query
from collector_utilities.type import URL
from model import SourceResponses


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


class BitbucketProjectBase(BitbucketBase, ABC):
    """Base class for Bitbucket collectors for a specific project."""

    async def _bitbucket_api_url(self, api: str) -> URL:
        """Return a Bitbucket API url for a project, if present in the parameters."""
        url = await super()._api_url()
        project = f"{self._parameter('owner')}/repos/{self._parameter('repository')}"
        api_url = URL(f"{url}/rest/api/1.0/projects/{project}" + (f"/{api}" if api else ""))
        return add_query(api_url, "limit=100&details=true")
