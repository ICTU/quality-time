"""Jira source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector
from collector_utilities.type import Response, URL

from .base import JiraBase


class JiraSourceVersion(JiraBase, SourceVersionCollector):
    """Jira source version collector."""

    async def _api_url(self) -> URL:
        """Extend to get the server info from Jira."""
        return URL(f"{await super()._api_url()}/rest/api/2/serverInfo")

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to return the Jira version."""
        return Version((await response.json())["version"])
