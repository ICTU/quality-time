"""Shared test data."""

from typing import cast

from internal.server_utilities.type import MetricId, ReportId, SourceId, SubjectId, NotificationDestinationId


METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
METRIC_ID3 = cast(MetricId, "metric_uuid3")
METRIC_ID4 = cast(MetricId, "metric_uuid4")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination_uuid")
REPORT_ID = cast(ReportId, "report_uuid")
REPORT_ID2 = cast(ReportId, "report_uuid2")
SOURCE_ID = cast(SourceId, "source_uuid")
SOURCE_ID2 = cast(SourceId, "source_uuid2")
SOURCE_ID3 = cast(SourceId, "source_uuid3")
SOURCE_ID4 = cast(SourceId, "source_uuid4")
SOURCE_ID5 = cast(SourceId, "source_uuid5")
SOURCE_ID6 = cast(SourceId, "source_uuid6")
SOURCE_ID7 = cast(SourceId, "source_uuid7")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
SUBJECT_ID2 = cast(SubjectId, "subject_uuid2")
SUBJECT_ID3 = cast(SubjectId, "subject_uuid3")

JOHN = dict(user="John", email="john@example.org")
JENNY = dict(user="Jenny", email="jenny@example.org")


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
                        target="0",
                        accept_debt=False,
                        tags=["security"],
                        scales=["count", "percentage"],
                        sources={
                            SOURCE_ID: dict(
                                type="source_type",
                                name="Source",
                                parameters=dict(url="https://url", password="password"),
                            )
                        },
                    )
                },
            )
        },
        notification_destinations={
            NOTIFICATION_DESTINATION_ID: dict(
                teams_webhook="", name="notification_destination", url="https://reporturl"
            )
        },
        issue_tracker=dict(type="jira", parameters=dict(username="jadoe", password="secret")),
    )
