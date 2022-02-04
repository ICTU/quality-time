"""Metric model class."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import cast

from typing import TYPE_CHECKING

from shared.utils.type import Direction, MetricId, Scale, Status, SubjectId, TargetType

from .source import Source


if TYPE_CHECKING:
    from .measurement import Measurement


class Metric(dict):
    """Class representing a metric."""

    def __init__(self, data_model, metric_data, metric_uuid: MetricId, subject_uuid: SubjectId = None) -> None:
        self.__data_model = data_model
        self.uuid = metric_uuid
        self.subject_uuid = subject_uuid

        source_data = metric_data.get("sources", {})
        self.sources_dict = self._instantiate_sources(source_data)
        self.sources = list(self.sources_dict.values())
        self.source_uuids = list(self.sources_dict.keys())

        super().__init__(metric_data)

    def __eq__(self, other):
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _instantiate_sources(self, source_data: dict) -> dict[str, Source]:
        """Create sources from source_data."""
        sources = {}
        for source_uuid, source_dict in source_data.items():
            sources[source_uuid] = Source(self.__data_model, source_dict, source_uuid, self.uuid)
        return sources

    def type(self) -> str | None:
        """Return the type of the metric."""
        return str(self["type"]) if "type" in self else None

    def status(self, last_measurement: Measurement | None) -> Status | None:
        """Determine the metric status."""
        if last_measurement and (status := last_measurement.status()):
            return status
        debt_end_date = self.get("debt_end_date") or date.max.isoformat()
        return "debt_target_met" if self.get("accept_debt") and date.today().isoformat() <= debt_end_date else None

    def issue_statuses(self, last_measurement: Measurement | None) -> list[dict]:
        """Return the metric's issue statuses."""
        last_issue_statuses = last_measurement.get("issue_status", []) if last_measurement else []
        return [status for status in last_issue_statuses if status["issue_id"] in self.get("issue_ids", [])]

    def addition(self):
        """Return the addition operator of the metric: sum, min, or max."""
        addition = self.get("addition") or self.__data_model["metrics"][self.type()]["addition"]
        return dict(max=max, min=min, sum=sum)[addition]

    def direction(self) -> Direction:
        """Return the direction of the metric: < or >."""
        return cast(Direction, self.get("direction") or self.__data_model["metrics"][self.type()]["direction"])

    def scale(self) -> Scale:
        """Return the current metric scale."""
        return cast(Scale, self.get("scale") or self.__data_model["metrics"][self.type()].get("default_scale", "count"))

    def scales(self) -> Sequence[Scale]:
        """Return the scales supported by the metric."""
        scales = self.__data_model.get("metrics", {}).get(self.type(), {}).get("scales", [])
        return cast(Sequence[Scale], scales)

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

    def summarize(self, measurements: list[Measurement], **kwargs):
        """Add a summary of the metric to the report."""
        latest_measurement = measurements[-1] if measurements else None
        summary = dict(self)
        summary["scale"] = self.scale()
        summary["status"] = self.status(latest_measurement)
        summary["status_start"] = latest_measurement.status_start() if latest_measurement else None
        summary["latest_measurement"] = latest_measurement
        summary["recent_measurements"] = [measurement.summarize(self.scale()) for measurement in measurements]
        if latest_measurement:
            summary["issue_status"] = self.issue_statuses(latest_measurement)
        summary.update(kwargs)
        return summary
