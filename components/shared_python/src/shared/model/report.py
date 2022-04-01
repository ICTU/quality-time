"""A class that represents a report."""

from typing import cast
from shared.model.source import Source

from shared.utils.type import Color, MetricId, ReportId, SourceId, Status, SubjectId

from .measurement import Measurement
from .subject import Subject
from .metric import Metric


STATUS_COLOR_MAPPING = cast(
    dict[Status, Color],
    dict(
        target_met="green",
        debt_target_met="grey",
        near_target_met="yellow",
        target_not_met="red",
    ),
)


class Report(dict):
    """Class representing a report."""

    def __init__(self, data_model, report_data: dict) -> None:
        """Instantiate a report."""
        self.__data_model = data_model

        subject_data = report_data.get("subjects", {})
        report_data["subjects"] = self._subjects(subject_data)
        super().__init__(report_data)

        self.subjects = list(self.subjects_dict.values())
        self.subject_uuids = set(self.subjects_dict.keys())

        self.metrics_dict = self._metrics()
        self.metrics = list(self.metrics_dict.values())

        self.sources_dict = self._sources()
        self.sources = list(self.sources_dict.values())

        if "_id" in self:
            self["_id"] = str(self["_id"])

    @property
    def metric_uuids(self) -> set[MetricId]:
        """Return only the metric ids."""
        return set(self.metrics_dict.keys())

    @property
    def source_uuids(self) -> set[SourceId]:
        """Return only the source ids."""
        return set(self.sources_dict.keys())

    @property
    def uuid(self):
        """Return the uuid of this report."""
        return cast(ReportId, self["report_uuid"])  # pragma: no cover-behave

    @property
    def subjects_dict(self) -> dict[SubjectId, Subject]:
        """Return the dict with subject uuids as keys and subject instances as values."""
        return self.get("subjects", {})

    @property
    def name(self) -> str:
        """A different access to title."""
        return self.get("title", "")

    def __eq__(self, other):
        """Return whether the reports are equal."""
        return self.uuid == other.uuid  # pragma: no cover-behave

    def _subjects(self, subject_data) -> dict[str, Subject]:
        """Instantiate subjects of this report."""
        subjects = {}
        for subject_uuid, subject in subject_data.items():
            if isinstance(subject, Subject):
                subjects[subject_uuid] = subject
            else:
                subjects[subject_uuid] = Subject(
                    self.__data_model, subject, subject_uuid, self
                )

        return subjects

    def _metrics(self) -> dict[MetricId, Metric]:
        """All metrics of all subjects of this report."""
        metrics = {}
        for subject in self.subjects:
            metrics.update(subject.metrics_dict)
        return metrics

    def _sources(self) -> dict[SourceId, Source]:
        """All sources of this report."""
        sources = {}
        for metric in self.metrics:
            sources.update(metric.sources_dict)
        return sources

    def summarize(self, measurements: dict[str, list[Measurement]]) -> dict:
        """Create a summary dict of this report."""
        summary = dict(self)
        summary["summary"] = dict(red=0, green=0, yellow=0, grey=0, white=0)
        summary["summary_by_subject"] = {}
        summary["summary_by_tag"] = {}

        summary["subjects"] = {
            subject.uuid: subject.summarize(measurements) for subject in self.subjects
        }

        for metric in self.metrics:
            latest_measurement = (
                measurements[metric.uuid][-1]
                if measurements and metric.uuid in measurements
                else None
            )
            metric_status = metric.status(latest_measurement)
            color = (
                STATUS_COLOR_MAPPING[metric_status]
                if metric_status is not None
                else "white"
            )
            summary["summary"][color] += 1
            summary["summary_by_subject"].setdefault(
                metric.subject_uuid, dict(red=0, green=0, yellow=0, grey=0, white=0)
            )[color] += 1
            for tag in metric.get("tags", []):
                summary["summary_by_tag"].setdefault(
                    tag, dict(red=0, green=0, yellow=0, grey=0, white=0)
                )[color] += 1

        return summary

    def instance_and_parents_for_uuid(
        self,
        metric_uuid: MetricId = None,
        source_uuid: SourceId = None,
    ) -> tuple | None:
        """Find an instance and it's parents.
        example:
        If a metric_uuid is provided,
        this function will return the metric, it's subject and it's report in that order:
        (Metric, Subject)

        Only one of the three uuid arguments should be filled.
        If more are filled, all but the first one will be ignored.
        """
        if metric_uuid is not None:
            metric = self.metrics_dict[metric_uuid]
            subject = self.subjects_dict[metric.subject_uuid]
            return (metric, subject)

        if source_uuid is not None:
            source = self.sources_dict[source_uuid]
            metric = source.metric
            subject = self.subjects_dict[metric.subject_uuid]
            return (source, metric, subject)
        return None  # pragma: no cover-behave
