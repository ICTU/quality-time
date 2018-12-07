"""CI-Jobs metrics."""

from quality_time.metric import Metric


class Jobs(Metric):
    """Number of CI-Jobs."""

    API = "jobs"


class FailedJobs(Metric):
    """Number of failed CI-Jobs."""

    API = "failed_jobs"
