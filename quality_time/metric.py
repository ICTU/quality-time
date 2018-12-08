"""Metric base class."""

import traceback
from typing import Optional, Tuple

from .api import API
from .type import ErrorMessage, Measurement, Measurements, MeasurementResponse


class Metric(API):
    """Base class for metrics."""

    @classmethod
    def get(cls, measurements: Measurements) -> MeasurementResponse:
        """Return the metric's measurement."""
        measurement, calculation_error = cls.safely_sum(measurements)
        return dict(metric=cls.name(), calculation_error=calculation_error, measurement=measurement)

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
