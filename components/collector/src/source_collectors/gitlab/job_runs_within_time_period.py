"""GitLab job runs within time period collector."""

from typing import TYPE_CHECKING, cast

from collector_utilities.date_time import days_ago

from .base import GitLabJobsBase

if TYPE_CHECKING:
    from model import Entity, SourceResponses

    from .json_types import Job


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
        lookback_days = int(cast(str, self._parameter("lookback_days")))
        result_types = cast(list[str], self._parameter("result_type"))
        build_age = days_ago(entity["build_datetime"])
        return build_age <= lookback_days and entity["build_result"] in result_types and super()._include_entity(entity)
