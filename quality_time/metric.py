"""Metric base class."""

import traceback
from typing import Optional, Tuple, Type

from quality_time.type import ErrorMessage, Measurement, Measurements


class Metric:
    """Base class for metrics."""

    API = "Subclass responsibility: name of the metric in the API"

    @classmethod
    def name(cls) -> str:
        """Return the name of the metric."""
        return cls.__name__

    @classmethod
    def safely_sum(cls, measurements: Measurements) -> Tuple[Optional[Measurement], Optional[ErrorMessage]]:
        """Return the summation of several measurements, without failing."""
        measurement, error = None, None
        if None not in measurements:
            try:
                measurement = cls.sum(measurements)
            except Exception:  # pylint: disable=broad-except
                error = ErrorMessage(traceback.format_exc())
        return measurement, error

    @classmethod
    def sum(cls, measurements: Measurements) -> Measurement:
        """Return the summation of several measurements."""
        return Measurement(sum([int(measurement) for measurement in measurements]))


def metric_registered_for(api_name: str) -> Type[Metric]:
    """Return the Metric subclass registered for the API name,"""
    return [cls for cls in Metric.__subclasses__() if cls.API == api_name][0]
