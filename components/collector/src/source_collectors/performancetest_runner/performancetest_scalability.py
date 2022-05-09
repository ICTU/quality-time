"""Performancetest-runner performancetest scalability collector."""

from collector_utilities.type import Response, Value
from model import SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerScalability(PerformanceTestRunnerBaseClass):
    """Collector for the scalability metric."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the scalability breaking point from the responses."""
        return str(min([await self.__breaking_point(response) for response in responses]))

    async def __breaking_point(self, response: Response) -> int:
        """Parse the breaking point from the response."""
        return int((await self._soup(response)).find(id="trendbreak_scalability").string)
