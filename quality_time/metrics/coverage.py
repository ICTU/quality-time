"""Test coverage metrics."""

from quality_time.metric import Metric, MetricStatus
from quality_time.type import Measurement


class CoveredLines(Metric):
    """Number of covered lines."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) > int(self.target()) else MetricStatus.target_not_met


class UncoveredLines(Metric):
    """Number of uncovered lines."""


class CoveredBranches(Metric):
    """Number of covered lines."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) > int(self.target()) else MetricStatus.target_not_met


class UncoveredBranches(Metric):
    """Number of uncovered lines."""
