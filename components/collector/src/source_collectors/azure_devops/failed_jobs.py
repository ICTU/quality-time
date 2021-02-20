"""Azure Devops failed jobs collector."""

from collector_utilities.type import Job

from .base import AzureDevopsJobs


class AzureDevopsFailedJobs(AzureDevopsJobs):
    """Collector for the failed jobs metric."""

    def _include_job(self, job: Job) -> bool:
        """Extend to check for failure type."""
        if not super()._include_job(job):
            return False
        return self._latest_build_result(job) in self._parameter("failure_type")
