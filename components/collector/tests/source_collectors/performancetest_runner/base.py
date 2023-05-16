"""Base classes for the Performancetest-runner collector unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class PerformanceTestRunnerTestCase(SourceCollectorTestCase):
    """Base class for testing the Performancetest-runner collectors."""

    SOURCE_TYPE = "performancetest_runner"
