"""cloc source version collector."""

from packaging.version import Version

from base_collectors import JSONFileSourceCollector, VersionCollector
from collector_utilities.type import Response


class ClocSourceVersion(JSONFileSourceCollector, VersionCollector):
    """Collector to collect the cloc version from the report."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the cloc version from the JSON."""
        json = await response.json(content_type=None)
        return Version(json["header"]["cloc_version"])
