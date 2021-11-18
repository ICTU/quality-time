"""A class that represents a Subject."""
from model.measurement import Measurement
from model.metric import Metric
from server_utilities.type import SubjectId

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from model.report import Report


class Subject(dict):
    """Class representing a report."""

    def __init__(self, data_model, subject_data: dict, subject_uuid: SubjectId, report: "Report") -> None:
        """Instantiate a Subject."""
        self.__data_model = data_model
        self.uuid = subject_uuid
        self.report = report

        metric_data = subject_data.get("metrics", {})
        self.metrics_dict = self._instantiate_metrics(metric_data)
        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

        super().__init__(subject_data)

    def __eq__(self, other):
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _instantiate_metrics(self, metric_data: dict) -> dict[str, Metric]:
        """Create metrics from metric_data."""
        metrics = {}
        for metric_uuid, metric_dict in metric_data.items():
            metrics[metric_uuid] = Metric(self.__data_model, metric_dict, metric_uuid, self.uuid)
        return metrics

    def name(self):
        """Either a custom name or one from the subject type in the data model."""
        return self.get("name") or self.__data_model["subjects"][self["type"]]["name"]

    def tag_subject(self, tag: str) -> Optional["Subject"]:
        """Return a Subject instance with only metrics belonging to one tag."""
        metrics = {metric.uuid: metric for metric in self.metrics if tag in metric.get("tags", [])}
        if len(metrics) == 0:
            return
        data = dict(self)
        data["metrics"] = metrics
        data["name"] = self.report["title"] + " ❯ " + self.name()
        return Subject(self.__data_model, data, self.uuid, tag)

    def summarize(self, measurements: dict[str, Measurement] | None):
        """Create a summary dict of this subject."""
        summary = dict(self)
        summary["metrics"] = {}
        for metric in self.metrics:
            metric_measurements = measurements[metric.uuid] if metric.uuid in measurements else None
            summary["metrics"][metric.uuid] = metric.summarize(metric_measurements)
        return summary
