"""Performancetest-runner performancetest scalability collector."""

from collector_utilities.type import Response, Value
from model import SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerScalability(PerformanceTestRunnerBaseClass):
    """Collector for the scalability metric."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the scalability breaking point from the responses."""
        breaking_points = [await self.__breaking_point_vusers(response) for response in responses]
        return str(min(breaking_points))

    async def _parse_total(self, responses: SourceResponses) -> Value:
        """Override to compute the total number of vusers from the responses."""
        breaking_points = [
            (await self.__breaking_point_vusers(response), await self.__breaking_point_percentage(response))
            for response in responses
        ]
        smallest_breaking_point_vusers, smallest_breaking_point_percentage = min(breaking_points)
        if smallest_breaking_point_percentage == 0:
            return "0"
        return str(round((smallest_breaking_point_vusers * 100) / smallest_breaking_point_percentage))

    async def __breaking_point_vusers(self, response: Response) -> int:
        """Parse the breaking point from the response."""
        return int((await self._soup(response)).find(id="trendbreak_scalability_vusers").string)

    async def __breaking_point_percentage(self, response: Response) -> int:
        """Parse the breaking point percentage from the response."""
        return int((await self._soup(response)).find(id="trendbreak_scalability").string)
