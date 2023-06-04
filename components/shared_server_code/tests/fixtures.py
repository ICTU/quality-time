"""Shared test data."""

from typing import cast

from shared.utils.type import MetricId, ReportId, SourceId, SubjectId, NotificationDestinationId

METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
SOURCE_ID = cast(SourceId, "source")
SOURCE_ID2 = cast(SourceId, "source2")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
REPORT_ID = cast(ReportId, "report_uuid")
REPORT_ID2 = cast(ReportId, "report_uuid2")

JOHN = dict(user="John", email="john@example.org", common_name="John Doe")
"""Fixtures for tests."""


def create_report(
    title: str = "Title", report_uuid: str = "report1", last: bool = True, deleted=None, metric_id: MetricId = METRIC_ID
) -> dict:
    """Returns a fake report."""
    report = dict(
        report_uuid=report_uuid,
        title=title,
        subjects={
            SUBJECT_ID: dict(
                name="Subject",
                type="subject_type",
                metrics={
                    metric_id: dict(
                        name="Metric",
                        type="violations",
                        addition="sum",
                        target="0",
                        accept_debt=False,
                        tags=["security"],
                        scale="count",
                        unit="foo",
                        webhook="www.webhook.com",
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
            NOTIFICATION_DESTINATION_ID: dict(webhook="", name="notification_destination", url="https://reporturl")
        },
        issue_tracker=dict(type="jira", parameters=dict(username="jadoe", password="secret")),
        last=last,
    )
    if deleted is not None:
        report.update({"deleted": deleted})
        return report

    return report
