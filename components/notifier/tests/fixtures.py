"""Fixtures for tests."""

from typing import cast

from shared.utils.type import MetricId, NotificationDestinationId, ReportId, SubjectId

METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
REPORT_ID = cast(ReportId, "report_uuid")
REPORT_ID2 = cast(ReportId, "report_uuid2")
SUBJECT_ID = cast(SubjectId, "subject_uuid")


def create_report_data(deleted: bool = False) -> dict:
    """Return data for a fake report."""
    report = {
        "report_uuid": REPORT_ID,
        "title": "Title",
        "subjects": {
            SUBJECT_ID: {
                "metrics": {
                    METRIC_ID: {
                        "name": "Metric",
                    },
                },
            },
        },
        "notification_destinations": {
            NOTIFICATION_DESTINATION_ID: {
                "webhook": "",
                "name": "notification_destination",
                "url": "https://reporturl",
            },
        },
        "last": True,
    }
    if deleted:
        report.update({"deleted": deleted})
    return report
