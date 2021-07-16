"""Performancetest-runner performancetest stability collector."""

from collector_utilities.type import Value
from model import SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerPerformanceTestStability(PerformanceTestRunnerBaseClass):
    """Collector for the performance test stability."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the trend break percentage from the responses and return the minimum percentage."""
        trend_breaks = []
        for response in responses:
            trend_breaks.append(int((await self._soup(response)).find(id="trendbreak_stability").string))
        return str(min(trend_breaks))
