"""A class that represents a subject."""

from typing import TYPE_CHECKING, cast

from shared.utils.type import MetricId, SubjectId

from .measurement import Measurement
from .metric import Metric

if TYPE_CHECKING:
    from .report import Report


class Subject(dict):  # noqa: PLW1641
    """Class representing a subject."""

    def __init__(self, data_model: dict, subject_data: dict, subject_uuid: SubjectId, report: "Report") -> None:
        """Instantiate a subject."""
        self.__data_model = data_model
        self.uuid = subject_uuid
        self.report = report

        metrics_data = subject_data.get("metrics", {})
        subject_data["metrics"] = self._instantiate_metrics(metrics_data)
        super().__init__(subject_data)

        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

    def __eq__(self, other: object) -> bool:
        """Return whether the subjects are equal."""
        return bool(self.uuid == other.uuid) if isinstance(other, Subject) else False  # pragma: no feature-test-cover

    def _instantiate_metrics(self, metric_data: dict) -> dict[str, Metric]:
        """Create metrics from metric_data."""
        metrics = {}
        for metric_uuid, metric_dict in metric_data.items():
            metrics[metric_uuid] = Metric(self.__data_model, metric_dict, metric_uuid, self.uuid)
        return metrics

    @property
    def type(self) -> str | None:
        """Return the type of the subject."""
        return str(self["type"]) if "type" in self else None

    @property
    def metrics_dict(self) -> dict[MetricId, Metric]:
        """Return the dict with metric uuids as keys and metric instances as values."""
        return cast(dict[MetricId, Metric], self.get("metrics", {}))

    @property
    def name(self) -> str | None:
        """Either a custom name or one from the subject type in the data model."""
        if name := self.get("name"):
            return str(name)
        default_name = self.__data_model["subjects"].get(self.type, {}).get("name")
        return str(default_name) if default_name else None

    def summarize(self, measurements: dict[MetricId, list[Measurement]]) -> dict:
        """Create a summary dict of this subject."""
        summary = dict(self)
        summary["metrics"] = {}
        for metric in self.metrics:
            metric_measurements = measurements.get(metric.uuid, [])
            metric_measurements = [measurement for measurement in metric_measurements if measurement.sources_exist()]
            summary["metrics"][metric.uuid] = metric.summarize(metric_measurements)
        return summary

    def delete_tag(self, tag: str) -> list[MetricId]:
        """Delete a tag from the subject and return the UUIDs of the affected metrics."""
        uuids = []
        for metric_uuid, metric in self.metrics_dict.items():
            if metric.delete_tag(tag):
                uuids.append(metric_uuid)
        return uuids

    def rename_tag(self, tag: str, new_tag: str) -> list[MetricId]:
        """Rename a tag in the report and return the UUIDs of the affected metrics."""
        uuids = []
        for metric_uuid, metric in self.metrics_dict.items():
            if metric.rename_tag(tag, new_tag):
                uuids.append(metric_uuid)
        return uuids
