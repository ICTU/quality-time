"""Performancetest-runner performancetest scalability collector."""

from base_collectors import SourceCollectorException
from collector_utilities.type import Value
from model import SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerScalability(PerformanceTestRunnerBaseClass):
    """Collector for the scalability metric."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the scalability breaking point from the responses."""
        trend_breaks = []
        for response in responses:
            breaking_point = int((await self._soup(response)).find(id="trendbreak_scalability").string)
            if breaking_point == 100:
                raise SourceCollectorException(
                    "No performance scalability breaking point occurred (breaking point is at 100%, expected < 100%)"
                )
            trend_breaks.append(breaking_point)
        return str(min(trend_breaks))
