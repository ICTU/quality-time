"""Test metrics."""

from quality_time.metric import Metric, MetricStatus
from quality_time.type import Measurement


class Tests(Metric):
    """Metric for the number of tests."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) > int(self.target()) else MetricStatus.target_not_met


class FailedTests(Metric):
    """Metric for the number of failed tests."""
