"""Performancetest-runner software version collector."""

from typing import cast

from bs4 import Tag
from packaging.version import Version

from base_collectors import VersionCollector
from collector_utilities.type import Response

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerSoftwareVersion(
    PerformanceTestRunnerBaseClass, VersionCollector
):
    """Collector for the software version analysed in the performance report."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        return Version(await self.__application_version(response))

    async def __application_version(self, response: Response) -> str:
        """Return the application version."""
        field = (await self._soup(response)).find(id="application_version")
        return cast(Tag, field).string or "" if field else ""
