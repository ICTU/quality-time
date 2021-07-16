"""Jenkins source up-to-dateness collector."""

from datetime import date

from model import SourceMeasurement, SourceResponses

from .base import JenkinsJobs


class JenkinsSourceUpToDateness(JenkinsJobs):
    """Collector to get the last build date from Jenkins jobs."""

    def _include_build(self, build) -> bool:
        """Override to only include builds with an allowed result type."""
        result_types = self._parameter("result_type")
        return str(build.get("result", "Not built")).capitalize().replace("_", " ") in result_types

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Extend to calculate how many days ago the jobs were built."""
        measurement = await super()._parse_source_responses(responses)
        build_dates = [entity["build_date"] for entity in measurement.entities if entity["build_date"]]
        measurement.value = str((date.today() - date.fromisoformat(max(build_dates))).days) if build_dates else None
        return measurement
