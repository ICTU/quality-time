"""GitLab failed jobs collector."""

from collector_utilities.type import URL, Job

from .base import GitLabJobsBase


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    async def _api_url(self) -> URL:
        """Extend to return only failed jobs."""
        return URL(str(await super()._api_url()) + "&scope=failed")

    def _count_job(self, job: Job) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return super()._count_job(job) and job["status"] in failure_types
