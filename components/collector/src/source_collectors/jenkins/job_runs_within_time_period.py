"""Jenkins job runs within time period collector."""

from typing import cast

from collector_utilities.date_time import datetime_from_timestamp, days_ago
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import JenkinsJobs
from .json_types import Build


class JenkinsJobRunsWithinTimePeriod(JenkinsJobs):
    """Collector class to measure the number of Jenkins jobs run within a specified time period."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Count the sum of jobs ran."""
        included_entities = [entity for entity in await self._parse_entities(responses) if self._include_entity(entity)]
        job_runs = [int(entity["build_count"]) for entity in included_entities]
        return SourceMeasurement(value=str(sum(job_runs)), entities=Entities(included_entities))

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        return Entities(
            [
                Entity(
                    key=job["name"],
                    name=job["name"],
                    url=job["url"],
                    build_count=str(len(self._builds(job))),
                )
                for job in self._jobs((await responses[0].json())["jobs"])
            ],
        )

    def _include_build(self, build: Build) -> bool:
        """Return whether to include this build or not."""
        result_types = [result_type.lower() for result_type in self._parameter("result_type")]
        lookback_days = int(cast(str, self._parameter("lookback_days")))
        build_datetime = datetime_from_timestamp(int(build["timestamp"]))
        return days_ago(build_datetime) <= lookback_days and build.get("result", "").lower() in result_types
