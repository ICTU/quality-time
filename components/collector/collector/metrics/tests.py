"""Test metrics."""

from collector.metric import Metric


class Tests(Metric):
    """Metric for the number of tests."""


class FailedTests(Metric):
    """Metric for the number of failed tests."""
