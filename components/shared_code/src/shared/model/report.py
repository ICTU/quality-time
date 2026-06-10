"""A class that represents a report."""

from typing import TYPE_CHECKING, cast

from shared.utils.type import Color, ItemId, MetricId, ReportId, SourceId, SourceLocationId, Status, SubjectId

from .subject import Subject

if TYPE_CHECKING:
    from shared.model.source import Source

    from .measurement import Measurement
    from .metric import Metric


STATUS_COLOR_MAPPING = cast(
    dict[Status, Color],
    {
        "target_met": "green",
        "debt_target_met": "grey",
        "near_target_met": "yellow",
        "target_not_met": "red",
        "informative": "blue",
    },
)


class Report(dict):  # noqa: PLW1641
    """Class representing a report."""

    def __init__(self, data_model: dict, report_data: dict) -> None:
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

        for metric in self.metrics:
            metric.source_locations = self.source_locations_dict

        if "_id" in self:  # pragma: no feature-test-cover
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
    def source_locations_dict(self) -> dict[SourceLocationId, dict]:
        """Return the dict with source location uuids as keys and source locations as values."""
        return cast(dict[SourceLocationId, dict], self.get("source_locations", {}))

    @property
    def source_location_uuids(self) -> set[SourceLocationId]:
        """Return only the source location ids."""
        return set(self.source_locations_dict.keys())

    @property
    def uuid(self) -> ReportId:
        """Return the uuid of this report."""
        return cast(ReportId, self["report_uuid"])  # pragma: no feature-test-cover

    @property
    def subjects_dict(self) -> dict[SubjectId, Subject]:
        """Return the dict with subject uuids as keys and subject instances as values."""
        return cast(dict[SubjectId, Subject], self.get("subjects", {}))

    @property
    def name(self) -> str:
        """A different access to title."""
        return cast(str, self.get("title", ""))

    def __eq__(self, other: object) -> bool:
        """Return whether the reports are equal."""
        return self.uuid == other.uuid if isinstance(other, self.__class__) else False  # pragma: no feature-test-cover

    def _subjects(self, subject_data: dict) -> dict[str, Subject]:
        """Instantiate subjects of this report."""
        return {
            subject_uuid: Subject(self.__data_model, subject, subject_uuid, self)
            for subject_uuid, subject in subject_data.items()
        }

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

    def summarize(self, measurements: dict[MetricId, list[Measurement]]) -> dict:
        """Create a summary dict of this report."""
        summary = dict(self)
        summary["summary"] = {"red": 0, "green": 0, "yellow": 0, "grey": 0, "blue": 0, "white": 0}
        summary["subjects"] = {subject.uuid: subject.summarize(measurements) for subject in self.subjects}

        for metric in self.metrics:
            latest_measurement = measurements[metric.uuid][-1] if measurements and metric.uuid in measurements else None
            metric_status = metric.status(latest_measurement)
            color = STATUS_COLOR_MAPPING[metric_status] if metric_status is not None else "white"
            summary["summary"][color] += 1
        return summary

    def metric_and_subject(self, metric_uuid: MetricId) -> tuple[Metric, Subject]:
        """Return the metric and its subject."""
        metric = self.metrics_dict[metric_uuid]
        subject = self.subjects_dict[metric.subject_uuid]
        return metric, subject

    def source_metric_and_subject(self, source_uuid: SourceId) -> tuple[Source, Metric, Subject]:
        """Return the source, its metric, and the metric's subject."""
        source = self.sources_dict[source_uuid]
        metric = source.metric
        subject = self.subjects_dict[metric.subject_uuid]
        return source, metric, subject

    def delete_tag(self, tag: str) -> list[ItemId]:
        """Delete a tag from the report and return the uuids of the affected subjects and metrics."""
        uuids = []
        for subject_uuid, subject in self.subjects_dict.items():
            if metric_uuids := subject.delete_tag(tag):
                uuids.extend([subject_uuid, *metric_uuids])
        return [self.uuid, *uuids] if uuids else []

    def rename_tag(self, tag: str, new_tag: str) -> list[ItemId]:
        """Rename a tag in the report and return the uuids of the affected subjects and metrics."""
        uuids = []
        for subject_uuid, subject in self.subjects_dict.items():
            if metric_uuids := subject.rename_tag(tag, new_tag):
                uuids.extend([subject_uuid, *metric_uuids])
        return [self.uuid, *uuids] if uuids else []


def get_metrics_from_reports(reports: list[Report]) -> dict[MetricId, Metric]:  # pragma: no feature-test-cover
    """Return the metrics from the reports.

    The metrics are augmented with the information from the report that is needed to measure them: the report uuid,
    the issue tracker, and the location parameters of the source locations that the sources of the metric refer to.
    """
    metrics: dict[MetricId, Metric] = {}

    for report in reports:
        metrics_dict: dict[MetricId, Metric] = report.metrics_dict.copy()
        for metric in metrics_dict.values():
            metric["report_uuid"] = report["report_uuid"]
            metric["issue_tracker"] = report.get("issue_tracker", {})
            for source in metric.sources:
                source["parameters"] = source.parameters_including_location()
        metrics.update(metrics_dict)
    return metrics
