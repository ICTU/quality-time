"""Measurement model class."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, cast

from model.metric import Metric
from model.source import Source
from server_utilities.functions import find_one, iso_timestamp, percentage
from server_utilities.type import Scale, SourceId, Status, TargetType


class Measurement(dict):  # lgtm [py/missing-equals]
    """Class representing a measurement."""

    # LGTM wants us to implement __eq__ because this class has extra instance attributes. However, the measurement
    # dictionary contains the metric UUID and thus we don't need to compare the instance attributes to know whether
    # two measurements are the same.

    def __init__(self, metric: Metric, *args, **kwargs) -> None:
        self.__previous_measurement: Optional[Measurement] = kwargs.pop("previous_measurement", None)
        self.__metric = metric
        super().__init__(*args, **kwargs)
        self["start"] = self["end"] = iso_timestamp()
        self["sources"] = [Source(self.__metric, source) for source in self["sources"]]

    def copy(self) -> Measurement:
        """Extend to return an instance of this class instead of a dict."""
        return self.__class__(self.__metric, super().copy(), previous_measurement=self)

    def set_target(self, scale: Scale, target_type: TargetType, value: Optional[str]) -> None:
        """Set the specified target for the scale."""
        self.setdefault(scale, {})[target_type] = value

    def status(self, scale: Scale) -> Optional[Status]:
        """Return the measurement status for the scale."""
        return cast(Optional[Status], self.get(scale, {}).get("status"))

    def status_start(self, scale: Scale) -> Optional[str]:
        """Return the start date of the status."""
        return str(self.get(scale, {}).get("status_start", "")) or None

    def debt_target_expired(self) -> bool:
        """Return whether the technical debt target is expired.

        Technical debt can expire because it was turned off or because the end date passed.
        """
        any_debt_target = any(self.get(scale, {}).get("debt_target") is not None for scale in self.__metric.scales())
        if not any_debt_target:
            return False
        return self.__metric.accept_debt_expired()

    def copy_entity_user_data(self, measurement: Measurement) -> None:
        """Copy the entity user data from the measurement to this measurement."""
        for new_source in self.sources():
            old_source = find_one(
                measurement.sources(), new_source["source_uuid"], lambda source: SourceId(source["source_uuid"])
            )
            if old_source:
                new_source.copy_entity_user_data(old_source)

    def update_measurement(self) -> None:
        """Update the measurement targets and scales."""
        self._update_targets()
        for scale in self.__metric.scales():
            self._update_scale(scale)

    def _update_scale(self, scale: Scale) -> None:
        """Update the measurement value and status for the scale."""
        self.setdefault(scale, {})["direction"] = self.__metric.direction()
        self[scale]["value"] = value = self._calculate_value(scale) if self._sources_ok() else None
        self._set_status(scale, self.__metric.status(value))

    def _calculate_value(self, scale: Scale) -> str:
        """Calculate the value of the measurement."""
        values = [source.value() for source in self.sources()]
        add = self.__metric.addition()
        if scale == "percentage":
            direction = self.__metric.direction()
            totals = [source.total() for source in self.sources()]
            if add is sum:
                values, totals = [sum(values)], [sum(totals)]
            values = [percentage(value, total, direction) for value, total in zip(values, totals)]
        return str(add(values))

    def _sources_ok(self) -> bool:
        """Return whether there are sources and none have parse or connection errors."""
        sources = self.sources()
        return bool(sources) and not any(source["parse_error"] or source["connection_error"] for source in sources)

    def _update_targets(self) -> None:
        """Update the measurement targets using the latest target values from the metric."""
        scale = self.__metric.scale()
        self.set_target(scale, "target", self.__metric.get_target("target"))
        self.set_target(scale, "near_target", self.__metric.get_target("near_target"))
        target_value = None if self.__metric.accept_debt_expired() else self.__metric.get_target("debt_target")
        self.set_target(scale, "debt_target", target_value)

    def _set_status(self, scale: Scale, status: Optional[str]) -> None:
        """Set the measurement status for the scale and the status start date."""
        self.setdefault(scale, {})["status"] = status
        if (previous := self.__previous_measurement) is None:
            return
        previous_status = previous.status(scale)
        if status_start := previous.status_start(scale) if status == previous_status else self["start"]:
            self[scale]["status_start"] = status_start

    def sources(self) -> Sequence[Source]:
        """Return the measurement's sources."""
        return cast(Sequence[Source], self["sources"])
