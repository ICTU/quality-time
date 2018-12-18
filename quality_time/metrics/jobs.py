"""CI-Jobs metrics."""

from quality_time.metric import FewerIsBetterMetric, MoreIsBetterMetric


class Jobs(MoreIsBetterMetric):
    """Number of CI-Jobs."""
    unit = "CI-jobs"


class FailedJobs(FewerIsBetterMetric):
    """Number of failed CI-Jobs."""
    unit = "failed CI-jobs"
