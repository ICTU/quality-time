"""Gatling source version collector."""

from packaging.version import Version

from base_collectors import VersionCollector
from collector_utilities.type import Response

from .base import GatlingHTMLCollector


class GatlingSourceVersion(GatlingHTMLCollector, VersionCollector):
    """Collector to collect the Gatling version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        return Version(await self.simulation_information(response, "Version") or "9999")
