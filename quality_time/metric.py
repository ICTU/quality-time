"""Metric base class."""

import traceback
from enum import auto, Enum
from typing import Dict, Optional, Tuple

from .api import API
from .type import ErrorMessage, Measurement, Measurements, Response


class MetricStatus(Enum):
    """Metric status."""
    target_met = auto()
    target_not_met = auto()


class Metric(API):
    """Base class for metrics."""

    default_target = Measurement("0")

    def get(self, response: Response) -> Response:
        """Return the metric's measurement."""
        metric_response: Dict[str, Optional[str]] = dict(default_target=self.default_target, target=self.target())
        metric_response.update(response)
        measurements = [source_response["measurement"] for source_response in response["source_responses"]]
        measurement, calculation_error = self.safely_sum(measurements)
        status = self.status(measurement).name if measurement is not None else None
        metric_response.update(dict(calculation_error=calculation_error, measurement=measurement, status=status))
        return metric_response

    def safely_sum(self, measurements: Measurements) -> Tuple[Optional[Measurement], Optional[ErrorMessage]]:
        """Return the summation of several measurements, without failing."""
        measurement, error = None, None
        if measurements and None not in measurements:
            try:
                measurement = self.sum(measurements)
            except Exception:  # pylint: disable=broad-except
                error = ErrorMessage(traceback.format_exc())
        return measurement, error

    def sum(self, measurements: Measurements) -> Measurement:  # pylint: disable=no-self-use
        """Return the summation of several measurements."""
        return Measurement(sum(int(measurement) for measurement in measurements))

    def target(self) -> Measurement:
        """Return the target value for the metric."""
        return self.query.get("target", self.default_target)

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) == int(self.target()) else MetricStatus.target_not_met


class MoreIsBetterMetric(Metric):
    """Class for metrics where higher values are better."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) >= int(self.target()) else MetricStatus.target_not_met


class FewerIsBetterMetric(Metric):
    """Class for metrics where lower values are better."""

    def status(self, measurement: Measurement) -> MetricStatus:
        """Return the status of the metric."""
        return MetricStatus.target_met if int(measurement) <= int(self.target()) else MetricStatus.target_not_met
