"""Measurement model class."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, cast

from model.metric import Metric
from model.source import Source
from server_utilities.functions import find_one, iso_timestamp, percentage
from server_utilities.type import Scale, SourceId, Status


class ScaleMeasurement(dict):
    """Class representing a measurement on a specific scale."""

    def __init__(self, *args, **kwargs):
        self.__previous_scale_measurement: Optional[ScaleMeasurement] = kwargs.pop("previous_scale_measurement")
        self._measurement: Measurement = kwargs.pop("measurement")
        self._metric: Metric = self._measurement.metric
        super().__init__(*args, **kwargs)

    def __set_status_start(self, status: Optional[str]) -> None:
        """Set the status start date."""
        if (previous := self.__previous_scale_measurement) is None:
            return
        if status_start := previous.status_start() if status == previous.status() else self._measurement["start"]:
            self["status_start"] = status_start

    def status(self) -> Optional[Status]:
        """Return the measurement status."""
        return cast(Optional[Status], self.get("status"))

    def status_start(self) -> Optional[str]:
        """Return the start date of the status."""
        return str(self.get("status_start", "")) or None

    def update_value_and_status(self) -> None:
        """Update the measurement value and status."""
        self["direction"] = self._metric.direction()
        self["value"] = value = self._calculate_value() if self._measurement.sources_ok() else None
        self["status"] = status = self._calculate_status(value)
        self.__set_status_start(status)

    def update_targets(self) -> None:
        """Update the measurement targets."""
        self["target"] = self._metric.get_target("target")
        self["near_target"] = self._metric.get_target("near_target")
        self["debt_target"] = None if self._metric.accept_debt_expired() else self._metric.get_target("debt_target")

    def _calculate_value(self) -> str:
        """Calculate the value of the measurement."""
        raise NotImplementedError

    def _calculate_status(self, measurement_value: Optional[str]) -> Optional[Status]:
        """Determined the status of the measurement."""
        if measurement_value is None:
            # Allow for accepted debt if there is no measurement yet so that the fact that a metric does not have a
            # source can be accepted as technical debt
            return None if self._metric.accept_debt_expired() or self._metric.sources() else "debt_target_met"
        value = float(measurement_value)
        better_or_equal = {">": float.__ge__, "<": float.__le__}[self["direction"]]
        if better_or_equal(value, self._target()):
            status: Status = "target_met"
        elif better_or_equal(value, self._debt_target()) and not self._metric.accept_debt_expired():
            status = "debt_target_met"
        elif better_or_equal(self._target(), self._near_target()) and better_or_equal(value, self._near_target()):
            status = "near_target_met"
        else:
            status = "target_not_met"
        return status

    def _target(self) -> float:
        return float(self.get("target") or 0)

    def _near_target(self) -> float:
        return float(self.get("near_target") or 0)

    def _debt_target(self) -> float:
        return float(self.get("debt_target") or 0)


class CountScaleMeasurement(ScaleMeasurement):
    """Measurement with a count scale."""

    def _calculate_value(self) -> str:
        """Override to calculate the value of the count scale measurement."""
        values = [source.value() for source in self._measurement.sources()]
        add = self._metric.addition()
        return str(add(values))


class PercentageScaleMeasurement(ScaleMeasurement):
    """Measurement with a percentage scale."""

    def _calculate_value(self) -> str:
        """Override to calculate the percentage."""
        values = [source.value() for source in self._measurement.sources()]
        totals = [source.total() for source in self._measurement.sources()]
        add = self._metric.addition()
        direction = self._metric.direction()
        if add is sum:
            values, totals = [sum(values)], [sum(totals)]
        values = [percentage(value, total, direction) for value, total in zip(values, totals)]
        return str(add(values))


class Measurement(dict):  # lgtm [py/missing-equals]
    """Class representing a measurement."""

    # LGTM wants us to implement __eq__ because this class has extra instance attributes. However, the measurement
    # dictionary contains the metric UUID and thus we don't need to compare the instance attributes to know whether
    # two measurements are the same.

    def __init__(self, metric: Metric, *args, **kwargs) -> None:
        self.__previous_measurement: Optional[Measurement] = kwargs.pop("previous_measurement", None)
        self.metric = metric
        super().__init__(*args, **kwargs)
        self["start"] = self["end"] = iso_timestamp()
        self["sources"] = [Source(self.metric, source) for source in self["sources"]]

    def scale_measurement(self, scale: Scale) -> ScaleMeasurement:
        """Create a measurement with a specific scale."""
        measurement_class = CountScaleMeasurement if scale == "count" else PercentageScaleMeasurement
        previous = None if self.__previous_measurement is None else self.__previous_measurement[scale]
        return measurement_class(self.get(scale, {}), measurement=self, previous_scale_measurement=previous)

    def copy(self) -> Measurement:
        """Extend to return an instance of this class instead of a dict."""
        return self.__class__(self.metric, super().copy(), previous_measurement=self)

    def __getitem__(self, item):
        """Override to convert the scale dictionary to a ScaleMeasurement instance before returning it."""
        if item in self.metric.scales() and not isinstance(self.get(item), ScaleMeasurement):
            self[item] = self.scale_measurement(item)
        return super().__getitem__(item)

    def debt_target_expired(self) -> bool:
        """Return whether the technical debt target is expired.

        Technical debt can expire because it was turned off or because the end date passed.
        """
        any_debt_target = any(self[scale].get("debt_target") is not None for scale in self.metric.scales())
        if not any_debt_target:
            return False
        return self.metric.accept_debt_expired()

    def copy_entity_user_data(self, measurement: Measurement) -> None:
        """Copy the entity user data from the measurement to this measurement."""
        for new_source in self.sources():
            old_source = find_one(
                measurement.sources(), new_source["source_uuid"], lambda source: SourceId(source["source_uuid"])
            )
            if old_source:
                new_source.copy_entity_user_data(old_source)

    def update_measurement(self) -> None:
        """Update the measurement targets, values, and statuses."""
        self[self.metric.scale()].update_targets()
        for scale in self.metric.scales():
            self[scale].update_value_and_status()

    def sources_ok(self) -> bool:
        """Return whether there are sources and none have parse or connection errors."""
        sources = self.sources()
        return bool(sources) and not any(source["parse_error"] or source["connection_error"] for source in sources)

    def sources(self) -> Sequence[Source]:
        """Return the measurement's sources."""
        return cast(Sequence[Source], self["sources"])
