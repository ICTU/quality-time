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
        self.__previous_measurement: Optional[Measurement] = kwargs.pop("previous_measurement", None)
        self.__metric = metric
        super().__init__(*args, **kwargs)
        self["start"] = self["end"] = iso_timestamp()

    def copy(self) -> Measurement:
        """Extend to return an instance of this class instead of a dict."""
        return self.__class__(self.__metric, super().copy(), previous_measurement=self)

    def set_previous_measurement(self, previous_measurement: Measurement):
        """Set the previous measurement."""
        self.__previous_measurement = previous_measurement

    def set_target(self, scale: Scale, target_type: TargetType, value: Optional[str]) -> None:
        """Set the specified target for the scale."""
        self.setdefault(scale, {})[target_type] = value

    def status(self, scale: Scale) -> Optional[Status]:
        """Return the measurement status for the scale."""
        return cast(Optional[Status], self.get(scale, {}).get("status"))

    def status_start(self, scale: Scale) -> Optional[str]:
        """Return the start date of the status."""
        return str(self.get(scale, {}).get("status_start", "")) or None

    def update_measurement(self) -> None:
        """Update the measurement targets and scales."""
        self._update_targets()
        for scale in self.__metric.scales():
            self._update_scale(scale)

    def _update_scale(self, scale: Scale) -> None:
        """Update the measurement value and status for the scale."""
        sources = self._sources()
        self.setdefault(scale, {})["direction"] = self.__metric.direction()
        if not sources or any(source["parse_error"] or source["connection_error"] for source in sources):
            value = None
        else:
            values = [source.value() for source in sources]
            add = self.__metric.addition()
            if scale == "percentage":
                direction = self.__metric.direction()
                totals = [source.total() for source in sources]
                if add is sum:
                    values, totals = [sum(values)], [sum(totals)]
                values = [percentage(value, total, direction) for value, total in zip(values, totals)]
            value = str(add(values))
        self[scale]["value"] = value
        self._set_status(scale, self.__metric.status(value))

    def _update_targets(self) -> None:
        """Update the measurement targets."""
        scale = self.__metric.scale()
        self.set_target(scale, "target", self.__metric.get_target("target"))
        self.set_target(scale, "near_target", self.__metric.get_target("near_target"))
        target_value = None if self.__metric.accept_debt_expired() else self.__metric.get_target("debt_target")
        self.set_target(scale, "debt_target", target_value)

    def _set_status(self, scale: Scale, status: Optional[str]) -> None:
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

    def _sources(self) -> Sequence[Source]:
        """Return the measurement's sources."""
        return [Source(self.__metric, source) for source in self["sources"]]
