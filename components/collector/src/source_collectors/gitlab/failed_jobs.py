"""GitLab failed jobs collector."""

from typing import TYPE_CHECKING, cast

from .base import GitLabJobsBase

if TYPE_CHECKING:
    from model import Entity, SourceResponses

    from .json_types import Job

FAILURE_COUNT = "failure_count"  # Key used to add the number of consecutive failures to the job JSON


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    async def _jobs(self, responses: SourceResponses) -> list[Job]:
        """Extend to add the number of consecutive failures to each job."""
        jobs = []
        for runs in (await self._job_runs(responses)).values():
            job = runs[0]
            job[FAILURE_COUNT] = self._consecutive_failures(runs)
            jobs.append(job)
        return jobs

    def _create_entity(self, job: Job) -> Entity:
        """Extend to add the number of consecutive failures to the entity."""
        entity = super()._create_entity(job)
        entity[FAILURE_COUNT] = str(job[FAILURE_COUNT])
        return entity

    def _consecutive_failures(self, runs: list[Job]) -> int:
        """Return the number of most recent runs of the job that failed in a row, within the look-back period."""
        failure_types = list(self._parameter("failure_type"))
        lookback_datetime = self._lookback_datetime()
        consecutive_failures = 0
        for run in runs:
            if run["status"] not in failure_types or self._build_datetime(run) < lookback_datetime:
                break
            consecutive_failures += 1
        return consecutive_failures

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the job has failed often enough."""
        minimum_number_of_failures = int(cast(str, self._parameter("minimum_number_of_failures")))
        return super()._include_entity(entity) and int(entity[FAILURE_COUNT]) >= minimum_number_of_failures
