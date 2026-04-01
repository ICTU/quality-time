"""Collectors for SonarQube."""

from typing import TYPE_CHECKING

from base_collectors import VersionCollector

from .base import SonarQubeProjectAnalysesBase

if TYPE_CHECKING:
    from collector_utilities.type import Response


class SonarQubeSoftwareVersion(SonarQubeProjectAnalysesBase, VersionCollector):
    """SonarQube software version collector."""

    async def _parse_source_response_version_string(self, response: Response) -> str:
        """Parse the version string from the source response."""
        return str((await response.json())["analyses"][0]["projectVersion"])
