"""GitLab unused jobs collector."""

from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Job

from .base import GitLabJobsBase


class GitLabUnusedJobs(GitLabJobsBase):
    """Collector class to get unused job counts from GitLab."""

    def _count_job(self, job: Job) -> bool:
        """Return whether the job is unused."""
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        return super()._count_job(job) and days_ago(parse(job["created_at"])) > max_days
