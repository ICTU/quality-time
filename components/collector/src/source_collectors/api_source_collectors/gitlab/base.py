"""GitLab collector base classes."""

from abc import ABC
from typing import Dict, Optional, Tuple

from base_collectors import SourceCollector
from collector_utilities.type import URL
from source_model import SourceResponses


class GitLabBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for GitLab collectors."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url with private token, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = f"{url}/api/v4/projects/{project}" + (f"/{api}" if api else "")
        sep = "&" if "?" in api_url else "?"
        api_url += f"{sep}per_page=100"
        return URL(api_url)

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to follow GitLab pagination links, if necessary."""
        responses = await super()._get_source_responses(*urls)
        next_urls = [
            next_url for response in responses if (next_url := response.links.get("next", {}).get("url"))
        ]  # pylint: disable=superfluous-parens
        if next_urls:
            responses.extend(await self._get_source_responses(*next_urls))
        return responses

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> Dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Private-Token"] = str(private_token)
        return headers
