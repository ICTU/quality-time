"""Performancetest-runner performancetest duration collector."""

from collector_utilities.type import Value
from model import SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerPerformanceTestDuration(PerformanceTestRunnerBaseClass):
    """Collector for the performance test duration."""

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the performance test durations from the responses and return the sum in minutes."""
        durations = []
        for response in responses:
            hours, minutes, seconds = [
                int(part) for part in (await self._soup(response)).find(id="duration").string.split(":", 2)
            ]
            durations.append(60 * hours + minutes + round(seconds / 60.0))
        return str(sum(durations))
