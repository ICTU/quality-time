"""Jenkins unused jobs collector."""

from datetime import datetime
from typing import cast

from collector_utilities.functions import days_ago
from collector_utilities.type import Job

from .base import JenkinsJobs


class JenkinsUnusedJobs(JenkinsJobs):
    """Collector to get unused jobs from Jenkins."""

    def _include_job(self, job: Job) -> bool:
        """Extend to count the job if its most recent build is too old."""
        if super()._include_job(job) and (build_datetime := self._build_datetime(job)) > datetime.min:
            max_days = int(cast(str, self._parameter("inactive_days")))
            return days_ago(build_datetime) > max_days
        return False
