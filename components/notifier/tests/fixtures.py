"""Fixtures for tests."""

from typing import cast

from shared.utils.type import MetricId, NotificationDestinationId, SubjectId

METRIC_ID = cast(MetricId, "metric_uuid")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
SUBJECT_ID = cast(SubjectId, "subject_uuid")


def create_report(deleted: bool = False) -> dict:
    """Return a fake report."""
    report = {
        "report_uuid": "report1",
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
    }
    if deleted:
        report.update({"deleted": deleted})
    return report
