"""Gatling source version collector."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector

from .base import GatlingHTMLCollector

if TYPE_CHECKING:
    from collector_utilities.type import Response


class GatlingSourceVersion(GatlingHTMLCollector, VersionCollector):
    """Collector to collect the Gatling version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        return Version(await self.simulation_information(response, "Version") or "9999")
