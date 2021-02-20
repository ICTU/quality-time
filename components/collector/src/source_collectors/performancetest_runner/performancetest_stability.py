"""Performancetest-runner performancetest stability collector."""

from source_model import SourceMeasurement, SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerPerformanceTestStability(PerformanceTestRunnerBaseClass):
    """Collector for the performance test stability."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the trend break percentage from the responses and return the minimum percentage."""
        trend_breaks = []
        for response in responses:
            trend_breaks.append(int((await self._soup(response)).find(id="trendbreak_stability").string))
        return SourceMeasurement(value=str(min(trend_breaks)))
