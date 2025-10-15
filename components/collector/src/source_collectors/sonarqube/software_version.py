"""Collectors for SonarQube."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector

from .base import SonarQubeProjectAnalysesBase

if TYPE_CHECKING:
    from collector_utilities.type import Response


class SonarQubeSoftwareVersion(SonarQubeProjectAnalysesBase, VersionCollector):
    """SonarQube software version collector."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        return Version((await response.json())["analyses"][0]["projectVersion"])
