"""Azure Devops unused jobs collector."""

from typing import cast

from collector_utilities.functions import days_ago
from collector_utilities.type import Job

from .base import AzureDevopsJobs


class AzureDevopsUnusedJobs(AzureDevopsJobs):
    """Collector for the unused jobs metric."""

    def _include_job(self, job: Job) -> bool:
        """Extend to filter unused jobs."""
        if not super()._include_job(job):
            return False
        max_days = int(cast(str, self._parameter("inactive_job_days")))
        actual_days = days_ago(self._latest_build_date_time(job))
        return actual_days > max_days
