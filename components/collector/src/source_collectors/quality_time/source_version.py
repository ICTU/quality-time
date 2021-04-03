"""Quality-time source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector
from collector_utilities.type import Response, URL


class QualityTimeSourceVersion(SourceVersionCollector):
    """Collector to get the source version from Quality-time."""

    async def _api_url(self) -> URL:
        """Extend to add the reports API path."""
        return URL(f"{await super()._api_url()}/api/v3/server")

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the response."""
        return Version((await response.json())["version"])
