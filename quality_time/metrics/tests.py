"""Test metrics."""

from quality_time.metric import FewerIsBetterMetric, MoreIsBetterMetric


class Tests(MoreIsBetterMetric):
    """Metric for the number of tests."""


class FailedTests(FewerIsBetterMetric):
    """Metric for the number of failed tests."""
