"""Fixture for reports."""

from typing import cast

from shared.utils.type import MetricId, NotificationDestinationId, ReportId, SourceId, SubjectId

METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
REPORT_ID = cast(ReportId, "report_uuid")
SOURCE_ID = cast(SourceId, "source_uuid")
SOURCE_ID2 = cast(SourceId, "source_uuid2")
SUBJECT_ID = cast(SubjectId, "subject_uuid")


def create_report(title: str = "Title", report_uuid: str = "report1", **kwargs) -> dict:
    """Return a fake report."""
    last: bool = True
    deleted = None
    metric_id: MetricId = METRIC_ID
    metric_type = "dependencies"
    source_type = "pip"
    measurement_requested = None

    for key, value in kwargs.items():
        match key:
            case "last":
                last = value
            case "deleted":
                deleted = value
            case "metric_id":
                metric_id = value
            case "metric_type":
                metric_type = value
            case "source_type":
                source_type = value
            case "measurement_requested":
                measurement_requested = value
            case _:
                raise ValueError

    metric = {
        metric_id: {
            "name": "Metric",
            "type": metric_type,
            "target": "0",
            "accept_debt": False,
            "scale": "count",
            "webhook": "www.webhook.com",
            "scales": ["count", "percentage"],
            "sources": {
                SOURCE_ID: {
                    "type": source_type,
                    "name": "Pip",
                    "parameters": {"url": "https://url", "password": "password"},  # nosec
                },
            },
            "measurement_requested": measurement_requested,
        },
    }

    report = {
        "report_uuid": report_uuid,
        "title": title,
        "subjects": {SUBJECT_ID: {"name": "Subject", "type": "subject_type", "metrics": metric}},
        "notification_destinations": {
            NOTIFICATION_DESTINATION_ID: {
                "webhook": "",
                "name": "notification_destination",
                "url": "https://reporturl",
            },
        },
        "issue_tracker": {"type": "jira", "parameters": {"username": "jadoe", "password": "secret"}},  # nosec
        "last": last,
    }

    if deleted is not None:
        report.update({"deleted": deleted})

    return report
