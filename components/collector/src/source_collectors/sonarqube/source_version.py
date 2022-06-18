"""SonarQube version collector."""

from packaging.version import Version

from base_collectors import VersionCollector
from collector_utilities.type import URL, Response


class SonarQubeSourceVersion(VersionCollector):
    """SonarQube source version collector."""

    async def _api_url(self) -> URL:
        """Extend to add the project analyses path and parameters."""
        url = await super()._api_url()
        return URL(f"{url}/api/server/version")

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the SonarQube version."""
        return Version(await response.text())
