"""Metric model class."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date
from typing import TYPE_CHECKING, cast

from shared.utils.functions import md5_hash
from shared.utils.type import (
    Direction,
    MetricId,
    Scale,
    SourceId,
    Status,
    SubjectId,
    TargetType,
)

from .source import Source

if TYPE_CHECKING:
    from .measurement import Measurement


class Metric(dict):  # noqa: PLW1641
    """Class representing a metric."""

    def __init__(
        self,
        data_model: dict,
        metric_data: dict,
        metric_uuid: MetricId,
        subject_uuid: SubjectId | None = None,
    ) -> None:
        self.__data_model = data_model
        self.uuid = metric_uuid
        self.subject_uuid = subject_uuid or cast(SubjectId, "")

        source_data = metric_data.get("sources", {})
        metric_data["sources"] = {
            source_uuid: Source(source_uuid, self, **source_dict) for source_uuid, source_dict in source_data.items()
        }
        super().__init__(metric_data)

        self.sources = list(self.sources_dict.values())
        self.source_uuids = list(self.sources_dict.keys())

    def __eq__(self, other: object) -> bool:
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid if isinstance(other, self.__class__) else False  # pragma: no feature-test-cover

    def type(self) -> str | None:
        """Return the type of the metric."""
        return str(self["type"]) if "type" in self else None

    @property
    def sources_dict(self) -> dict[SourceId, Source]:
        """Return the dict with source_uuid as keys and source instances as values."""
        return cast(dict[SourceId, Source], self.get("sources", {}))

    @property
    def name(self) -> str | None:
        """Either a custom name or one from the metric type in the data model."""
        if name := self.get("name"):
            return str(name)
        default_name = self.__data_model["metrics"].get(self.type(), {}).get("name")
        return str(default_name) if default_name else None

    @property
    def unit(self) -> str:
        """Either a custom unit or one from the metric type in the data model."""
        return cast(str, self.get("unit") or self.__data_model["metrics"].get(self.type(), {}).get("unit"))

    def evaluate_targets(self) -> bool:
        """Return whether the metric is to evaluate its targets. If not, it is considered to be informative."""
        return bool(self.get("evaluate_targets", True))

    def status(self, last_measurement: Measurement | None) -> Status | None:
        """Determine the metric status."""
        if last_measurement and (status := last_measurement.status()):
            return status
        return "debt_target_met" if self.accept_debt() and not self.debt_end_date_passed() else None

    def issue_statuses(self, last_measurement: Measurement | None) -> list[dict]:
        """Return the metric's issue statuses."""
        last_issue_statuses = last_measurement.get("issue_status", []) if last_measurement else []
        return [status for status in last_issue_statuses if status["issue_id"] in self.issue_ids()]

    def issue_ids(self) -> list[str]:
        """Return the ids of this metric's issues."""
        return cast(list[str], self.get("issue_ids", []))

    def addition(self) -> Callable:
        """Return the addition operator of the metric: sum, min, or max."""
        addition = self.get("addition") or self.__data_model["metrics"][self.type()]["addition"]
        # The cast works around https://github.com/python/mypy/issues/10740
        return cast(Callable, {"max": max, "min": min, "sum": sum}[addition])

    def direction(self) -> Direction:
        """Return the direction of the metric: < or >."""
        return cast(
            Direction,
            self.get("direction") or self.__data_model["metrics"][self.type()]["direction"],
        )

    def scale(self) -> Scale:
        """Return the current metric scale."""
        return cast(
            Scale,
            self.get("scale") or self.__data_model["metrics"][self.type()].get("default_scale", "count"),
        )

    def scales(self) -> Sequence[Scale]:
        """Return the scales supported by the metric."""
        scales = self.__data_model.get("metrics", {}).get(self.type(), {}).get("scales", [])
        return cast(Sequence[Scale], scales)

    def accept_debt(self) -> bool:
        """Return whether the metric has its technical debt accepted."""
        return bool(self.get("accept_debt", False))

    def debt_end_date(self) -> str:
        """Return the end date of the accepted technical debt."""
        return str(self.get("debt_end_date") or date.max.isoformat())

    def debt_end_date_passed(self) -> bool:
        """Return whether the end date of the accepted technical debt has passed."""
        # The debt end date is a date in ISO-format without timezone information; suppress the Ruff error
        return date.today().isoformat() > self.debt_end_date()  # noqa: DTZ011

    def get_target(self, target_type: TargetType) -> str | None:
        """Return the target."""
        target = self.get(target_type)
        return str(target) if target else None

    def get_measured_attribute(self, source: Source) -> tuple[str | None, str]:
        """Return the attribute of the source entities that is used to measure the value, and its type.

        For example, when using Jira as source for user story points, the points of user stories (the source entities)
        are summed to arrive at the total number of user story points.
        """
        source_type = self.sources_dict[source["source_uuid"]]["type"]
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

    def summarize(self, measurements: list[Measurement], **kwargs) -> dict:
        """Add a summary of the metric to the report."""
        latest_measurement = measurements[-1] if measurements else None
        summary = dict(self)
        summary["scale"] = self.scale()
        summary["status"] = self.status(latest_measurement)
        summary["status_start"] = latest_measurement.status_start() if latest_measurement else None
        summary["latest_measurement"] = latest_measurement.summarize_latest() if latest_measurement else None
        summary["recent_measurements"] = [measurement.summarize() for measurement in measurements]
        if latest_measurement:
            summary["issue_status"] = self.issue_statuses(latest_measurement)
        summary.update(kwargs)
        return summary

    def source_parameter_hash(self) -> str:  # pragma: no feature-test-cover
        """Return a hash of the source parameters that can be used to check for changed parameters."""
        sources = [source for _, source in sorted(self.sources_dict.items())]  # Make hash independent of source order
        source_parameters = [source.get("parameters") for source in sources]
        return md5_hash(str(source_parameters))

    def delete_tag(self, tag: str) -> bool:
        """Delete a tag from the metric if the metric has it. Return whether the metric was affected."""
        if tag in self.get("tags", []):
            self["tags"].remove(tag)
            return True
        return False

    def rename_tag(self, tag: str, new_tag: str) -> bool:
        """Rename a tag in the metric if the metric has it. Return whether the metric was affected."""
        if tag in self.get("tags", []):
            self["tags"].remove(tag)
            if new_tag not in self["tags"]:
                self["tags"].append(new_tag)
            return True
        return False
