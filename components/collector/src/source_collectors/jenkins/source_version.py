"""Jenkins source version collector."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector

if TYPE_CHECKING:
    from collector_utilities.type import Response


class JenkinsSourceVersion(VersionCollector):
    """Collector class to measure the version of a Jenkins instance."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to return the Jenkins version."""
        return Version(response.headers["X-Jenkins"])
