"""Jenkins failed jobs collector."""

from collector_utilities.type import Job

from .base import JenkinsJobs


class JenkinsFailedJobs(JenkinsJobs):
    """Collector to get failed jobs from Jenkins."""

    def _include_job(self, job: Job) -> bool:
        """Extend to count the job if its build status matches the failure types selected by the user."""
        return super()._include_job(job) and self._build_status(job) in self._parameter("failure_type")
