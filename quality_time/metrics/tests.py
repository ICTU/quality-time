"""Test metrics."""

from quality_time.metric import Metric


class Tests(Metric):
    """Metric for the number of tests."""

    API = "tests"


class FailedTests(Metric):
    """Metric for the number of failed tests."""

    API = "failed_tests"
    