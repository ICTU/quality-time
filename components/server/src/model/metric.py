"""Metric model class."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Optional, cast

from model.source import Source
from server_utilities.functions import find_one
from server_utilities.type import Direction, MetricId, Scale, Status, TargetType


class Metric:
    """Class representing a metric."""

    def __init__(self, data_model, metric_data, metric_uuid: MetricId) -> None:
        self.__data_model = data_model
        self.__data = metric_data
        self.uuid = metric_uuid

    def __eq__(self, other):
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid

    def type(self) -> str:
        """Return the type of the metric."""
        return str(self.__data["type"])

    def addition(self):
        """Return the addition operator of the metric: sum, min, or max."""
        return dict(max=max, min=min, sum=sum)[self.__data["addition"]]

    def direction(self) -> Direction:
        """Return the direction of the metric: < or >."""
        return cast(Direction, self.__data.get("direction") or self.__data_model["metrics"][self.type()]["direction"])

    def scale(self) -> Scale:
        """Return the current metric scale."""
        return cast(Scale, self.__data.get("scale", "count"))

    def scales(self) -> Sequence[Scale]:
        """Return the scales supported by the metric."""
        return cast(Sequence[Scale], self.__data_model["metrics"][self.type()]["scales"])

    def accept_debt(self) -> bool:
        """Return whether the metric has its technical debt accepted."""
        return bool(self.__data.get("accept_debt", False))

    def accept_debt_expired(self) -> bool:
        """Return whether the accepted debt has expired."""
        return not self.accept_debt() or date.today().isoformat() > self.debt_end_date()

    def debt_end_date(self) -> str:
        """Return the end date of the accepted technical debt."""
        return str(self.__data.get("debt_end_date")) or date.max.isoformat()

    def target(self) -> float:
        """Return the metric target value."""
        return float(
            self.__data.get("target", self.__data_model.get("metric", {}).get(self.type(), {}).get("target")) or 0
        )

    def near_target(self) -> float:
        """Return the metric near target value."""
        return float(self.__data.get("near_target") or 0)

    def debt_target(self) -> float:
        """Return the metric debt target value."""
        return float(self.__data.get("debt_target") or 0)

    def get_target(self, target_type: TargetType) -> Optional[str]:
        """Return the target."""
        target = self.__data.get(target_type)
        return str(target) if target else None

    def status(self, measurement_value: Optional[str]) -> Optional[Status]:
        """Return the metric status, given a measurement value."""
        if measurement_value is None:
            # Allow for accepted debt if there is no measurement yet so that the fact that a metric does not have a
            # source can be accepted as technical debt
            return None if self.accept_debt_expired() or self.sources() else "debt_target_met"
        value = float(measurement_value)
        better_or_equal = {">": float.__ge__, "<": float.__le__}[self.direction()]
        if better_or_equal(value, self.target()):
            status: Status = "target_met"
        elif better_or_equal(value, self.debt_target()) and not self.accept_debt_expired():
            status = "debt_target_met"
        elif better_or_equal(self.target(), self.near_target()) and better_or_equal(value, self.near_target()):
            status = "near_target_met"
        else:
            status = "target_not_met"
        return status

    def sources(self) -> dict:
        """Return the metric sources."""
        return cast(dict, self.__data.get("sources", {}))

    def get_measured_attribute(self, source: Source) -> tuple[Optional[str], str]:
        """Return the attribute of the source entities that is used to measure the value, and its type.

        For example, when using Jira as source for user story points, the points of user stories (the source entities)
        are summed to arrive at the total number of user story points.
        """
        source_type = self.sources()[source["source_uuid"]]["type"]
        entity_type = self.__data_model["sources"][source_type]["entities"].get(self.type(), {})
        attribute = entity_type.get("measured_attribute")
        measured_attribute = None if attribute is None else str(attribute)
        attribute_type = self._get_measured_attribute_type(entity_type, measured_attribute)
        return measured_attribute, attribute_type

    @staticmethod
    def _get_measured_attribute_type(entity: dict[str, list[dict[str, str]]], attribute_key: Optional[str]) -> str:
        """Look up the type of an entity attribute."""
        attribute = find_one(entity.get("attributes", []), attribute_key, lambda attr: attr["key"]) or {}
        return str(attribute.get("type", "text"))
