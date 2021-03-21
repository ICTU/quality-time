"""Measurement model class."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, cast

from model.metric import Metric
from model.source import Source
from server_utilities.functions import iso_timestamp, percentage
from server_utilities.type import Scale, Status, TargetType


class Measurement(dict):
    """Class representing a measurement."""

    def __init__(self, metric: Metric, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__metric = metric
        self.__previous_measurement: Optional[Measurement] = None
        self["start"] = self["end"] = iso_timestamp()

    @classmethod
    def copy_from(cls, previous_measurement: Measurement) -> Measurement:
        """Create a measurement from a previous measurement."""
        new_measurement = previous_measurement.copy()
        new_measurement.set_previous_measurement(previous_measurement)
        return new_measurement

    def copy(self) -> Measurement:
        """Extend to return an instance of this class instead of a dict."""
        return self.__class__(self.__metric, super().copy())

    def set_previous_measurement(self, previous_measurement: Measurement):
        """Set the previous measurement."""
        self.__previous_measurement = previous_measurement

    def set_target(self, scale: Scale, target_type: TargetType, value: Optional[str]) -> None:
        """Set the specified target for the scale."""
        self.setdefault(scale, {})[target_type] = value

    def status(self, scale: Scale) -> Optional[Status]:
        """Return the measurement status for the scale."""
        return cast(Optional[Status], self.get(scale, {}).get("status"))

    def set_status(self, scale: Scale, status: Optional[str]) -> None:
        """Set the measurement status for the scale and the status start date."""
        self.setdefault(scale, {})["status"] = status
        if self.__previous_measurement is None:
            status_start = None
        else:
            previous_status = self.__previous_measurement.status(scale)
            status_start = (
                self.__previous_measurement.status_start(scale) if status == previous_status else self["start"]
            )
        if status_start:
            self[scale]["status_start"] = status_start

    def status_start(self, scale: Scale) -> Optional[str]:
        """Return the start date of the status."""
        return str(self.get(scale, {}).get("status_start", "")) or None

    def sources(self) -> Sequence[Source]:
        """Return the measurement's sources."""
        return [Source(self.__metric, source) for source in self["sources"]]

    def update_value(self, scale: Scale) -> Optional[str]:
        """Update the measurement value from the source measurements and return it."""
        sources = self.sources()
        self.setdefault(scale, {})["direction"] = self.__metric.direction()
        if not sources or any(source["parse_error"] or source["connection_error"] for source in sources):
            self[scale]["value"] = None
            return None
        values = [source.value() for source in sources]
        add = self.__metric.addition()
        if scale == "percentage":
            direction = self.__metric.direction()
            totals = [source.total() for source in sources]
            if add is sum:
                values, totals = [sum(values)], [sum(totals)]
            values = [percentage(value, total, direction) for value, total in zip(values, totals)]
        self.setdefault(scale, {})["value"] = value = str(add(values))
        return value
