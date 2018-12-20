"""Test metrics."""

from quality_time.metric import FewerIsBetterMetric, MoreIsBetterMetric


class Tests(MoreIsBetterMetric):
    """Metric for the number of tests."""
    name = "Number of tests"
    unit = "tests"


class FailedTests(FewerIsBetterMetric):
    """Metric for the number of failed tests."""
    name = "Number of failed tests"
    unit = "failed tests"
