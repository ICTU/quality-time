"""Performancetest-runner source up-to-dateness collector."""

from typing import TYPE_CHECKING, cast

from bs4 import Tag

from base_collectors import TimePassedCollector
from collector_utilities.date_time import datetime_from_parts

from .base import PerformanceTestRunnerBaseClass

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class PerformanceTestRunnerSourceUpToDateness(PerformanceTestRunnerBaseClass, TimePassedCollector):
    """Collector for the performance test report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the start date time of the test from the response."""
        start = await self.__start_of_the_test(response)
        year, month, day, hour, minute, second = (int(part) for part in start.split("."))
        return datetime_from_parts(year, month, day, hour, minute, second)

    async def __start_of_the_test(self, response: Response) -> str:
        """Return the start of the test field."""
        field = (await self._soup(response)).find(id="start_of_the_test")
        return cast(Tag, field).string or "" if field else ""
