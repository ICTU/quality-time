"""Shared test data."""

from typing import cast

from shared.utils.type import ItemId, MetricId, NotificationDestinationId, ReportId, SourceId, SubjectId

METRIC_ID = cast(MetricId, "metric_uuid")
NOTIFICATION_DESTINATION_ID = cast(NotificationDestinationId, "destination1")
SOURCE_ID = cast(SourceId, "source")
SOURCE_ID2 = cast(SourceId, "source2")
SOURCE_LOCATION_ID = cast(ItemId, "source_location_uuid")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
REPORT_ID = cast(ReportId, "report_uuid")


def create_source_location(**kwargs) -> dict:
    """Return a fake source location."""
    return {
        "location_name": "Source location",
        "source_type": "sonarqube",
        "url": "https://url",
        "landing_url": "",
        "username": "",
        "password": "password",  # nosec
        "private_token": "",
    } | kwargs


def create_report(
    title: str = "Title",
    report_uuid: str = "report1",
    last: bool = True,
    metric_id: MetricId = METRIC_ID,
) -> dict:
    """Return a fake report."""
    return {
        "report_uuid": report_uuid,
        "title": title,
        "source_locations": {SOURCE_LOCATION_ID: create_source_location()},
        "subjects": {
            SUBJECT_ID: {
                "name": "Subject",
                "type": "subject_type",
                "metrics": {
                    metric_id: {
                        "name": "Metric",
                        "type": "violations",
                        "target": "0",
                        "accept_debt": False,
                        "tags": ["security"],
                        "scale": "count",
                        "webhook": "www.webhook.com",
                        "scales": ["count", "percentage"],
                        "sources": {
                            SOURCE_ID: {
                                "type": "sonarqube",
                                "name": "Source",
                                "source_location": SOURCE_LOCATION_ID,
                                "parameters": {"tags": ["security"]},
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
        "issue_tracker": {"type": "jira", "parameters": {"username": "jadoe", "password": "secret"}},  # nosec
        "last": last,
    }
