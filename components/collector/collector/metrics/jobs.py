"""CI-Jobs metrics."""

from collector.metric import Metric


class Jobs(Metric):
    """Number of CI-Jobs."""


class FailedJobs(Metric):
    """Number of failed CI-Jobs."""
