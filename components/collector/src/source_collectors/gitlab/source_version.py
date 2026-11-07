"""GitLab source version collector."""

from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version

from base_collectors import VersionCollector

from .base import GitLabBase

if TYPE_CHECKING:
    from collector_utilities.type import URL, Response


class GitLabSourceVersion(GitLabBase, VersionCollector):
    """Collector class to measure the version of a GitLab instance."""

    async def _api_url(self) -> URL:
        """Override to return the version API URL."""
        return await super()._api_url() / "api/v4/version"

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to return the GitLab version."""
        version_string = (await response.json())["version"]
        try:
            return Version(version_string)
        except InvalidVersion:
            return Version(version_string.split("-")[0])
