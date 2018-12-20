"""CI-Jobs metrics."""

from quality_time.metric import FewerIsBetterMetric, MoreIsBetterMetric


class Jobs(MoreIsBetterMetric):
    """Number of CI-Jobs."""
    name = "Number of CI-jobs"
    unit = "CI-jobs"


class FailedJobs(FewerIsBetterMetric):
    """Number of failed CI-Jobs."""
    name = "Number of failed CI-jobs"
    unit = "failed CI-jobs"
