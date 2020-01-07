"""Shared test data."""

from typing import cast

from server_utilities.type import MetricId, ReportId, SourceId, SubjectId


METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
REPORT_ID = cast(ReportId, "report_uuid")
SOURCE_ID = cast(SourceId, "source_uuid")
SOURCE_ID2 = cast(SourceId, "source_uuid2")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
SUBJECT_ID2 = cast(SubjectId, "subject_uuid2")


def create_report():
    """Return a test report."""
    return dict(
        _id=REPORT_ID,
        report_uuid=REPORT_ID,
        title="Report",
        subjects={
            SUBJECT_ID: dict(
                name="Subject",
                type="subject_type",
                metrics={
                    METRIC_ID: dict(
                        name="Metric",
                        type="metric_type",
                        addition="sum",
                        accept_debt=False,
                        tags=[],
                        sources={
                            SOURCE_ID: dict(
                                type="source_type",
                                name="Source")})})})
