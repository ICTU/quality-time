"""Performancetest-runner source code version collector."""

from packaging.version import Version

from base_collectors import VersionCollector
from collector_utilities.type import Response

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerSourceCodeVersion(PerformanceTestRunnerBaseClass, VersionCollector):
    """Collector for the source code version analysed in the performance."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        return Version((await self._soup(response)).find(id="application_version").string)
