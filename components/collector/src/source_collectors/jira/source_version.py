"""Jira source version collector."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector

from .base import JiraBase

if TYPE_CHECKING:
    from collector_utilities.type import URL, Response


class JiraSourceVersion(JiraBase, VersionCollector):
    """Jira source version collector."""

    async def _api_url(self) -> URL:
        """Extend to get the server info from Jira."""
        return await super()._api_url() / f"rest/api/{self._rest_api_version}/serverInfo"

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to return the Jira version."""
        return Version((await response.json())["version"])
