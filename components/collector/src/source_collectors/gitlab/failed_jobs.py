"""GitLab failed jobs collector."""

from collector_utilities.type import Job

from .base import GitLabJobsBase


class GitLabFailedJobs(GitLabJobsBase):
    """Collector class to get failed job counts from GitLab."""

    def _count_job(self, job: Job) -> bool:
        """Return whether the job has failed."""
        failure_types = list(self._parameter("failure_type"))
        return super()._count_job(job) and job["status"] in failure_types
