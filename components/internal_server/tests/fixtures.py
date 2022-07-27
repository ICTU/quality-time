"""Shared test data."""

from typing import cast

from shared.utils.type import MetricId, ReportId, SourceId, SubjectId, NotificationDestinationId


METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination_uuid")
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
                        type="violations",
                        addition="sum",
                        target="0",
                        accept_debt=False,
                        tags=["security"],
                        scales=["count", "percentage"],
                        sources={
                            SOURCE_ID: dict(
                                type="sonarqube",
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
