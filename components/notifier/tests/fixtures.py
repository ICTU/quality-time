"""Fixtures for tests."""

from typing import cast

from shared.utils.type import MetricId, NotificationDestinationId, SourceId, SubjectId

METRIC_ID = cast(MetricId, "metric_uuid")
METRIC_ID2 = cast(MetricId, "metric_uuid2")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
SOURCE_ID = cast(SourceId, "source_uuid")
SUBJECT_ID = cast(SubjectId, "subject_uuid")


def create_report(
    title: str = "Title",
    report_uuid: str = "report1",
    last: bool = True,
    deleted: bool | None = None,
    metric_id: MetricId = METRIC_ID,
) -> dict:
    """Return a fake report."""
    report = {
        "report_uuid": report_uuid,
        "title": title,
        "subjects": {
            SUBJECT_ID: {
                "name": "Subject",
                "type": "subject_type",
                "metrics": {
                    metric_id: {
                        "name": "Metric",
                        "type": "violations",
                        "addition": "sum",
                        "target": "0",
                        "accept_debt": False,
                        "tags": ["security"],
                        "scale": "count",
                        "unit": "foo",
                        "webhook": "www.webhook.com",
                        "scales": ["count", "percentage"],
                        "sources": {
                            SOURCE_ID: {
                                "type": "sonarqube",
                                "name": "Source",
                                "parameters": {"url": "https://url", "password": "password"},
                            },
                        },
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
        "issue_tracker": {"type": "jira", "parameters": {"username": "jadoe", "password": "secret"}},
        "last": last,
    }
    if deleted is not None:
        report.update({"deleted": deleted})
        return report

    return report
