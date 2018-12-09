"""CI-Jobs metrics."""

from quality_time.metric import Metric, MetricStatus
from quality_time.type import Measurement


class Jobs(Metric):
    """Number of CI-Jobs."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) > int(self.target()) else MetricStatus.target_not_met


class FailedJobs(Metric):
    """Number of failed CI-Jobs."""
