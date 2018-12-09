"""Metric base class."""

import traceback
from enum import Enum
from typing import Optional, Tuple

from .api import API
from .type import ErrorMessage, Measurement, Measurements, MeasurementResponse


class MetricStatus(Enum):
    """Metric status."""
    target_met = 0
    target_not_met = 1


class Metric(API):
    """Base class for metrics."""

    default_target = Measurement("0")

    def __init__(self, requested_target: Measurement = None) -> None:
        super().__init__()
        self.requested_target = requested_target

    def get(self, measurements: Measurements) -> MeasurementResponse:
        """Return the metric's measurement."""
        measurement, calculation_error = self.safely_sum(measurements)
        target = self.target()
        status = self.status(measurement).name if measurement is not None else None
        return dict(calculation_error=calculation_error, measurement=measurement, default_target=self.default_target,
                    target=target, status=status)

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

    def target(self) -> Measurement:
        """Return the target value for the metric."""
        return self.default_target if self.requested_target is None else self.requested_target

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) <= int(self.target()) else MetricStatus.target_not_met
        