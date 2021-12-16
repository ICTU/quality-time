"""A class that represents a report."""

from typing import cast

from internal.model.measurement import Measurement
from internal.model.subject import Subject
from internal.model.metric import Metric
from internal.server_utilities.type import Color, ReportId, Status


STATUS_COLOR_MAPPING = cast(
    dict[Status, Color],
    dict(target_met="green", debt_target_met="grey", near_target_met="yellow", target_not_met="red"),
)


class Report(dict):
    """Class representing a report."""

    def __init__(self, data_model, report_data: dict) -> None:
        """Instantiate a report."""
        self.__data_model = data_model

        subject_data = report_data.get("subjects", {})
        self.subjects_dict = self._subjects(subject_data)
        self.subjects = list(self.subjects_dict.values())

        self.metrics_dict = self._metrics()
        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

        report_data["_id"] = str(report_data["_id"])

        super().__init__(report_data)

    @property
    def uuid(self):
        """Return the uuid of this report."""
        return cast(ReportId, self["report_uuid"])  # pragma: no cover-behave

    def __eq__(self, other):
        """Return whether the reports are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _subjects(self, subject_data) -> dict[str, Subject]:
        """Instantiate subjects of this report."""
        subjects = {}
        for subject_uuid, subject in subject_data.items():
            subjects[subject_uuid] = Subject(self.__data_model, subject, subject_uuid, self)

        return subjects

    def _metrics(self) -> dict[str, Metric]:
        """All metrics of all subjects of this report."""
        metrics = {}
        for subject in self.subjects:
            metrics.update(subject.metrics_dict)
        return metrics
