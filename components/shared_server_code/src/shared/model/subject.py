"""A class that represents a subject."""

from typing import TYPE_CHECKING, Optional

from shared.utils.type import MetricId, SubjectId

from .measurement import Measurement
from .metric import Metric


if TYPE_CHECKING:
    from .report import Report


class Subject(dict):
    """Class representing a subject."""

    def __init__(self, data_model, subject_data: dict, subject_uuid: SubjectId, report: "Report") -> None:
        """Instantiate a subject."""
        self.__data_model = data_model
        self.uuid = subject_uuid
        self.report = report

        metrics_data = subject_data.get("metrics", {})
        subject_data["metrics"] = self._instantiate_metrics(metrics_data)
        super().__init__(subject_data)

        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

    def __eq__(self, other):
        """Return whether the subjects are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

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
        return self.get("metrics", {})

    @property
    def name(self):
        """Either a custom name or one from the subject type in the data model."""
        return self.get("name") or self.__data_model["subjects"].get(self.type, {}).get("name")

    def tag_subject(self, tag: str) -> Optional["Subject"]:
        """Return a Subject instance with only metrics belonging to one tag."""
        metrics = {metric.uuid: metric for metric in self.metrics if tag in metric.get("tags", [])}
        if len(metrics) == 0:
            return None
        data = dict(self)
        data["metrics"] = metrics
        data["name"] = self.report.name + " ❯ " + self.name
        return Subject(self.__data_model, data, self.uuid, self.report)

    def summarize(self, measurements: dict[MetricId, list[Measurement]]):
        """Create a summary dict of this subject."""
        summary = dict(self)
        summary["metrics"] = {}
        for metric in self.metrics:
            metric_measurements = measurements.get(metric.uuid, [])
            metric_measurements = [measurement for measurement in metric_measurements if measurement.sources_exist()]
            summary["metrics"][metric.uuid] = metric.summarize(metric_measurements)
        return summary
