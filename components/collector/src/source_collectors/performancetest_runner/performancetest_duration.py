"""Performancetest-runner performancetest duration collector."""

from source_model import SourceMeasurement, SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerPerformanceTestDuration(PerformanceTestRunnerBaseClass):
    """Collector for the performance test duration."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the performance test durations from the responses and return the sum in minutes."""
        durations = []
        for response in responses:
            hours, minutes, seconds = [
                int(part) for part in (await self._soup(response)).find(id="duration").string.split(":", 2)
            ]
            durations.append(60 * hours + minutes + round(seconds / 60.0))
        return SourceMeasurement(value=str(sum(durations)))
