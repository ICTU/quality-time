from typing import cast
from model.measurement import Measurement
from model.subject import Subject
from server_utilities.type import Color, ReportId, Status


STATUS_COLOR_MAPPING = cast(
    dict[Status, Color],
    dict(target_met="green", debt_target_met="grey", near_target_met="yellow", target_not_met="red"),
)


class Report(dict):
    """Class representing a report."""

    def __init__(self, data_model, report_data: dict) -> None:
        """Instantiate a Report."""
        self.__data_model = data_model
        self.uuid = cast(ReportId, report_data["report_uuid"])

        subject_data = report_data.pop("subjects")
        self.subjects_dict = self._subjects(subject_data)
        self.subjects = list(self.subjects_dict.values())
        self.subject_uuids = list(self.subjects_dict.keys())

        self.metrics_dict = self._metrics(self.subjects)
        self.metrics = list(self.metrics_dict.values())
        self.metric_uuids = list(self.metrics_dict.keys())

        report_data["_id"] = str(report_data["_id"])

        super().__init__(report_data)

    def __eq__(self, other):
        """Return whether the metrics are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _subjects(self, subject_data) -> tuple[set, set]:
        """Instantiate subjects of this report."""
        subjects = {}
        for subject_uuid, subject_dict in subject_data.items():
            subjects[subject_uuid] = Subject(self.__data_model, subject_dict, subject_uuid, self.uuid)

        return subjects

    def _metrics(self, subjects: list[Subject]) -> tuple[set, set]:
        """All metrics of all subjects of this report."""
        metrics = {}
        for subject in subjects:
            metrics.update(subject.metrics_dict)
        return metrics

    def summarize(self, measurements: dict[str, Measurement] | None) -> dict:
        """Create a summary dict of this report."""

        summary = dict(self)
        summary["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=0)
        summary["summary_by_subject"] = {}
        summary["summary_by_tag"] = {}

        summary["subjects"] = {subject.uuid: subject.summarize(measurements) for subject in self.subjects}

        for metric in self.metrics:
            metric_measurements = measurements[metric.uuid]
            color = STATUS_COLOR_MAPPING.get(metric.status(metric_measurements[-1]), "white")
            summary["summary"][color] += 1
            summary["summary_by_subject"].setdefault(
                metric.subject_uuid, dict(red=0, green=0, yellow=0, grey=0, white=0)
            )[color] += 1
            for tag in metric.get("tags", []):
                summary["summary_by_tag"].setdefault(tag, dict(red=0, green=0, yellow=0, grey=0, white=0))[color] += 1

        return summary
