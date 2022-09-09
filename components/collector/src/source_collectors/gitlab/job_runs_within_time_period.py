"""GitLab job runs within time period collector."""

from collections.abc import Sequence
from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Job
from model import SourceResponses

from .base import GitLabJobsBase


class GitLabJobRunsWithinTimePeriod(GitLabJobsBase):
    """Collector class to measure the amount of GitLab CI builds ran within a specified time period."""

    async def _jobs(self, responses: SourceResponses) -> Sequence[Job]:
        """Return the jobs to count, not deduplicated to latest branch or tag run."""
        jobs: list[Job] = []
        for response in responses:
            jobs.extend(list(await response.json()))
        return [job for job in jobs if self._count_job(job)]

    def _count_job(self, job: Job) -> bool:
        """Return whether the job was ran within the specified time period."""
        within_time_period = days_ago(parse(job["created_at"])) <= int(
            cast(str, self._parameter(parameter_key="lookback_days")))
        return within_time_period and super()._count_job(job)
