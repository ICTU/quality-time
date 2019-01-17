"""Metric base class."""

import traceback
from typing import Optional, Tuple

from .api import API
from .type import ErrorMessage, Measurement, Measurements, Response


class Metric(API):
    """Base class for metrics."""

    def get(self, response: Response) -> Response:
        """Return the metric's measurement."""
        metric_response: Response = dict()
        metric_response.update(response)
        measurements = [source_response["measurement"] for source_response in response["source"]["responses"]]
        measurement, calculation_error = self.safely_sum(measurements)
        metric_response["measurement"] = dict(calculation_error=calculation_error, measurement=measurement)
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
