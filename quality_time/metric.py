import traceback
from typing import Optional, Sequence, Tuple

from quality_time.type import ErrorMessage, Measurement, Measurements


class Metric:
    """Base class for metrics."""

    @classmethod
    def name(cls) -> str:
        """Return the name of the metric."""
        return cls.__name__

    @classmethod
    def safely_sum(cls, measurements: Measurements) -> Tuple[Optional[Measurement], Optional[ErrorMessage]]: 
        measurement, error = None, None
        try:
            measurement = cls.sum(measurements)
        except Exception:
            error = ErrorMessage(traceback.format_exc())
        return measurement, error

    @classmethod
    def sum(cls, measurements: Measurements) -> Measurement:
        """Return the summation of several measurements."""
        return Measurement(sum([int(measurement) for measurement in measurements]))