"""Jenkins source up-to-dateness collector."""

from typing import TYPE_CHECKING

from collector_utilities.date_time import days_ago

from .base import JenkinsJobs

if TYPE_CHECKING:
    from model import SourceMeasurement, SourceResponses

    from .json_types import Build


class JenkinsSourceUpToDateness(JenkinsJobs):
    """Collector to get the last build date from Jenkins jobs."""

    def _include_build(self, build: Build) -> bool:
        """Override to only include builds with an allowed result type."""
        result_types = self._parameter("result_type")
        return str(build.get("result", "Not built")).capitalize().replace("_", " ") in result_types

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Extend to calculate how many days ago the jobs were built."""
        measurement = await super()._parse_source_responses(responses)
        build_datetimes = [ent["build_datetime"] for ent in measurement.get_entities() if ent["build_datetime"]]
        measurement.value = str(days_ago(max(build_datetimes))) if build_datetimes else None
        return measurement
