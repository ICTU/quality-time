"""GitLab job runs within time period collector."""

from typing import cast

from collector_utilities.date_time import days_ago, parse_datetime
from collector_utilities.type import Job
from model import Entity, SourceResponses

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
        build_age = days_ago(parse_datetime(entity["build_date"]))
        within_time_period = build_age <= int(cast(str, self._parameter("lookback_days")))
        return within_time_period and super()._include_entity(entity)
