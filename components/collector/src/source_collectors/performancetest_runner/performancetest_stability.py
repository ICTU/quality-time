"""Performancetest-runner performancetest stability collector."""

from typing import cast

from bs4 import Tag

from collector_utilities.type import Response, Value
from model import SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerPerformanceTestStability(PerformanceTestRunnerBaseClass):
    """Collector for the performance test stability."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the trend break percentage from the responses and return the minimum percentage."""
        trend_breaks = [
            int(await self.__trendbreak_stability(response)) for response in responses
        ]
        return str(min(trend_breaks))

    async def __trendbreak_stability(self, response: Response) -> str:
        """Return the trendbreak stability."""
        field = (await self._soup(response)).find(id="trendbreak_stability")
        return cast(Tag, field).string or "" if field else ""
