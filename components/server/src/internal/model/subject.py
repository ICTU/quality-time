"""A class that represents a subject."""

from typing import TYPE_CHECKING, Optional

from internal.model.metric import Metric
from internal.server_utilities.type import SubjectId


if TYPE_CHECKING:
    from internal.model.report import Report


class Subject(dict):
    """Class representing a subject."""

    def __init__(self, data_model, subject_data: dict, subject_uuid: SubjectId, report: Optional["Report"]) -> None:
        """Instantiate a subject."""
        self.__data_model = data_model
        self.uuid = subject_uuid
        self.report = report if report is not None else {}

        metric_data = subject_data.get("metrics", {})
        self.metrics_dict = self._instantiate_metrics(metric_data)
        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

        super().__init__(subject_data)

    def __eq__(self, other):
        """Return whether the subjects are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _instantiate_metrics(self, metric_data: dict) -> dict[str, Metric]:
        """Create metrics from metric_data."""
        metrics = {}
        for metric_uuid, metric_dict in metric_data.items():
            metrics[metric_uuid] = Metric(self.__data_model, metric_dict, metric_uuid, self.uuid)
        return metrics
