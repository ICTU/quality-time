"""Performancetest-runner software version collector."""

from typing import TYPE_CHECKING, cast

from bs4 import Tag

from base_collectors import VersionCollector

from .base import PerformanceTestRunnerBaseClass

if TYPE_CHECKING:
    from collector_utilities.type import Response


class PerformanceTestRunnerSoftwareVersion(PerformanceTestRunnerBaseClass, VersionCollector):
    """Collector for the software version analysed in the performance report."""

    async def _parse_source_response_version_string(self, response: Response) -> str:
        """Parse the version string from the source response."""
        field = (await self._soup(response)).find(id="application_version")
        return cast(Tag, field).string or "" if field else ""
