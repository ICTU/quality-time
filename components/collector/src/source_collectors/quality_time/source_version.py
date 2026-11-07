"""Quality-time source version collector."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector

if TYPE_CHECKING:
    from collector_utilities.type import URL, Response


class QualityTimeSourceVersion(VersionCollector):
    """Collector to get the source version from Quality-time."""

    EXTERNAL_API_VERSION = "v3"

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        return await super()._api_url() / f"api/{self.EXTERNAL_API_VERSION}/server"

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the response."""
        return Version((await response.json())["version"])
