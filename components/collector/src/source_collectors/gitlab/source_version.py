"""GitLab source version collector."""

from packaging.version import InvalidVersion, Version

from base_collectors import SourceVersionCollector
from collector_utilities.type import Response, URL

from .base import GitLabBase


class GitLabSourceVersion(GitLabBase, SourceVersionCollector):
    """Collector class to measure the version of a GitLab instance."""

    async def _api_url(self) -> URL:
        """Override to return the version API URL."""
        return URL(f"{await super()._api_url()}/api/v4/version")

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to return the GitLab version."""
        version_string = (await response.json())["version"]
        try:
            return Version(version_string)
        except InvalidVersion:
            return Version(version_string.split("-")[0])
