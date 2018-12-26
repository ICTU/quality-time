"""Source version metrics."""

from distutils.version import LooseVersion

from collector.metric import MoreIsBetterMetric, MetricStatus
from collector.type import Measurement, Measurements


class Version(MoreIsBetterMetric):
    """Version of a metric source."""

    name = "Version"

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if LooseVersion(measurement) >= LooseVersion(self.target()) \
            else MetricStatus.target_not_met

    def sum(self, measurements: Measurements) -> Measurement:
        """Return the summation of several measurements."""
        if len(measurements) > 1:
            raise ValueError("Can't add version numbers")
        return measurements[0]
