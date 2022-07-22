"""Jenkins job runs within time period collector."""

from base_collectors import SourceCollector
from model import SourceMeasurement, SourceResponses


class JenkinsJobRunsWithinTimePeriod(SourceCollector):
    """Collector class to measure the amount of Jenkins jobs run within a specified time period."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Count the sum of jobs ran."""
        return SourceMeasurement(value=0)  # TODO
