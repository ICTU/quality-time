"""GitLab job runs within time period collector."""

from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Job
from model import SourceResponses, Entity

from .base import GitLabJobsBase


class GitLabJobRunsWithinTimePeriod(GitLabJobsBase):
    """Collector class to measure the number of GitLab CI builds run within a specified time period."""

    @staticmethod
    async def _jobs(responses: SourceResponses) -> list[Job]:
        """Return the jobs to count, not deduplicated to latest branch or tag run."""
        jobs: list[Job] = []
        for response in responses:
            jobs.extend(list(await response.json()))
        return jobs

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job was run within the specified time period."""
        within_time_period = days_ago(parse(entity["build_date"])) <= int(
            cast(str, self._parameter("lookback_days")))
        return within_time_period and super()._include_entity(entity)
