"""Performancetest-runner performancetest scalability collector."""

from typing import cast

from bs4 import Tag

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
        """Override to compute the total number of virtual users from the responses."""
        breaking_points = [
            (
                await self.__breaking_point_vusers(response),
                await self.__max_vusers(response),
            )
            for response in responses
        ]
        return str(min(breaking_points)[1])

    async def __breaking_point_vusers(self, response: Response) -> int:
        """Parse the breaking point from the response."""
        return int(await self.__get_element_by_id("trendbreak_scalability_vusers", response))

    async def __max_vusers(self, response: Response) -> int:
        """Parse the maximum numer of virtual users from the response."""
        return int(await self.__get_element_by_id("virtual_users", response))

    async def __get_element_by_id(self, element_id: str, response: Response) -> str:
        """Parse the element with the given id from the response."""
        field = (await self._soup(response)).find(id=element_id)
        return cast(Tag, field).string or "" if field else ""
