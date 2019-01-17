"""Source version metrics."""

from collector.metric import MoreIsBetterMetric
from collector.type import Measurement, Measurements


class Version(MoreIsBetterMetric):
    """Version of a metric source."""

    name = "Version"

    def sum(self, measurements: Measurements) -> Measurement:
        """Return the summation of several measurements."""
        if len(measurements) > 1:
            raise ValueError("Can't add version numbers")
        return measurements[0]
