"""Source version metrics."""

from distutils.version import LooseVersion

from quality_time.metric import Metric, MetricStatus
from quality_time.type import Measurement, Measurements


class Version(Metric):
    """Version of a metric source."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if LooseVersion(measurement) >= LooseVersion(self.target()) \
            else MetricStatus.target_not_met

    @classmethod
    def sum(cls, measurements: Measurements) -> Measurement:
        """Return the summation of several measurements."""
        if len(measurements) > 1:
            raise ValueError("Can't add version numbers")
        return measurements[0]
