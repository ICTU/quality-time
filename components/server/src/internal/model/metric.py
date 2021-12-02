"""Metric model class."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import cast

from internal.model.source import Source
from internal.server_utilities.type import Direction, MetricId, Scale, TargetType


class Metric(dict):
    """Class representing a metric."""

    def __init__(self, data_model, metric_data, metric_uuid: MetricId) -> None:
        self.__data_model = data_model
        self.uuid = metric_uuid
        super().__init__(metric_data)

    def __eq__(self, other):
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def type(self) -> str:
        """Return the type of the metric."""
        return str(self["type"])

    def addition(self):
        """Return the addition operator of the metric: sum, min, or max."""
        addition = self.get("addition") or self.__data_model["metrics"][self.type()]["addition"]
        return dict(max=max, min=min, sum=sum)[addition]

    def direction(self) -> Direction:
        """Return the direction of the metric: < or >."""
        return cast(Direction, self.get("direction") or self.__data_model["metrics"][self.type()]["direction"])

    def scale(self) -> Scale:
        """Return the current metric scale."""
        return cast(Scale, self.get("scale") or self.__data_model["metrics"][self.type()]["default_scale"])

    def scales(self) -> Sequence[Scale]:
        """Return the scales supported by the metric."""
        return cast(Sequence[Scale], self.__data_model["metrics"][self.type()]["scales"])

    def accept_debt(self) -> bool:
        """Return whether the metric has its technical debt accepted."""
        return bool(self.get("accept_debt", False))

    def accept_debt_expired(self) -> bool:
        """Return whether the accepted debt has expired."""
        return not self.accept_debt() or date.today().isoformat() > self.debt_end_date()

    def debt_end_date(self) -> str:
        """Return the end date of the accepted technical debt."""
        return str(self.get("debt_end_date")) or date.max.isoformat()

    def get_target(self, target_type: TargetType) -> str | None:
        """Return the target."""
        target = self.get(target_type)
        return str(target) if target else None

    def sources(self) -> dict:
        """Return the metric sources."""
        return cast(dict, self.get("sources", {}))

    def get_measured_attribute(self, source: Source) -> tuple[str | None, str]:
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
    def _get_measured_attribute_type(entity: dict[str, list[dict[str, str]]], attribute_key: str | None) -> str:
        """Look up the type of an entity attribute."""
        attribute = {attr["key"]: attr for attr in entity.get("attributes", [])}.get(str(attribute_key), {})
        return str(attribute.get("type", "text"))
