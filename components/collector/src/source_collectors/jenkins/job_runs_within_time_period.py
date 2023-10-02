"""Jenkins job runs within time period collector."""

from typing import cast

from collector_utilities.date_time import datetime_fromtimestamp, days_ago
from collector_utilities.type import Job
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import JenkinsJobs


class JenkinsJobRunsWithinTimePeriod(JenkinsJobs):
    """Collector class to measure the number of Jenkins jobs run within a specified time period."""

    def _include_build(self, build) -> bool:
        """Return whether to include this build or not."""
        build_datetime = datetime_fromtimestamp(int(build["timestamp"] / 1000.0))
        return days_ago(build_datetime) <= int(cast(str, self._parameter("lookback_days")))

    def _builds_within_timeperiod(self, job: Job) -> int:
        """Return the number of job builds within time period."""
        return len(super()._builds(job))

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        return Entities(
            [
                Entity(
                    key=job["name"],
                    name=job["name"],
                    url=job["url"],
                    build_count=self._builds_within_timeperiod(job),
                )
                for job in self._jobs((await responses[0].json())["jobs"])
            ],
        )

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Count the sum of jobs ran."""
        included_entities = [entity for entity in await self._parse_entities(responses) if self._include_entity(entity)]
        job_runs = [job["build_count"] for job in included_entities]
        return SourceMeasurement(value=str(sum(job_runs)), entities=Entities(included_entities))
