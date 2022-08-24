"""Jenkins job runs within time period collector."""

from datetime import datetime

from collector_utilities.functions import days_ago
from collector_utilities.type import Job
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import JenkinsJobs


class JenkinsJobRunsWithinTimePeriod(JenkinsJobs):
    """Collector class to measure the amount of Jenkins jobs run within a specified time period."""

    def _include_build(self, build) -> bool:
        """Return whether to include this build or not."""
        build_datetime = datetime.utcfromtimestamp(int(build["timestamp"] / 1000.0))
        return days_ago(build_datetime) <= int(self._parameter(parameter_key="lookback_days"))

    def _builds_within_timeperiod(self, job: Job) -> int:
        """Return the amount of job builds within timeperiod."""
        return len([build for build in job.get("builds", []) if self._include_build(build)])

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the jobs."""
        entities = Entities(
            [
                Entity(
                    key=job["name"],
                    name=job["name"],
                    url=job["url"],
                    build_count=self._builds_within_timeperiod(job),
                )
                for job in self._jobs((await responses[0].json())["jobs"])
            ]
        )
        return entities

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Count the sum of jobs ran."""
        parsed_entities = await self._parse_entities(responses)
        job_runs = [job['build_count'] for job in parsed_entities]
        return SourceMeasurement(value=str(sum(job_runs)), entities=parsed_entities)
