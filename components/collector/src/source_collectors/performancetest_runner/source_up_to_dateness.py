"""Performancetest-runner source up-to-dateness collector."""

from datetime import datetime

from base_collectors import TimePassedCollector
from collector_utilities.type import Response

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerSourceUpToDateness(PerformanceTestRunnerBaseClass, TimePassedCollector):
    """Collector for the performance test report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the start date time of the test from the response."""
        datetime_parts = [
            int(part) for part in (await self._soup(response)).find(id="start_of_the_test").string.split(".")
        ]
        return datetime(*datetime_parts)  # type: ignore
