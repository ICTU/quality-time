"""Source version metrics."""

from quality_time.metric import Metric
from quality_time.type import Measurement, Measurements


class Version(Metric):
    """Version of a metric source."""

    @classmethod
    def sum(cls, measurements: Measurements) -> Measurement:
        """Return the summation of several measurements."""
        return Measurement(", ".join(measurements))
