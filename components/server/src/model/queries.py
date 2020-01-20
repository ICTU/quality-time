"""Model queries."""

from typing import cast, Any, List, Optional, Tuple

from server_utilities.type import MetricId, ReportId, SourceId, SubjectId


def get_report_uuid(reports, subject_uuid: SubjectId) -> Optional[ReportId]:
    """Return the uuid of the report that contains the subject with the specified uuid."""
    return cast(ReportId, [report for report in reports if subject_uuid in report["subjects"]][0]["report_uuid"])


def get_subject_uuid(reports, metric_uuid: MetricId) -> Optional[SubjectId]:
    """Return the uuid of the subject that has the metric with the specified uuid."""
    subjects: List[Tuple[SubjectId, Any]] = []
    for report in reports:
        subjects.extend(report["subjects"].items())
    return [subject_uuid for (subject_uuid, subject) in subjects if metric_uuid in subject["metrics"]][0]


def get_metric_uuid(reports, source_uuid: SourceId) -> Optional[MetricId]:
    """Return the uuid of the metric that has a source with the specified uuid."""
    metrics: List[Tuple[MetricId, Any]] = []
    for report in reports:
        for subject in report["subjects"].values():
            metrics.extend(subject["metrics"].items())
    return [metric_uuid for (metric_uuid, metric) in metrics if source_uuid in metric["sources"]][0]
