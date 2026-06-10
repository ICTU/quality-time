"""Shared test data."""

from typing import cast

from shared.utils.type import ItemId, MetricId, ReportId, SourceId, SubjectId, NotificationDestinationId


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
SOURCE_LOCATION_ID = cast(ItemId, "source_location_uuid")
SOURCE_LOCATION_ID2 = cast(ItemId, "source_location_uuid2")
SUBJECT_ID = cast(SubjectId, "subject_uuid")
SUBJECT_ID2 = cast(SubjectId, "subject_uuid2")

JOHN = {"user": "John", "email": "john@example.org", "common_name": "John Doe"}
JENNY = {"user": "Jenny", "email": "jenny@example.org", "common_name": "Jenny Doe"}


def create_source_location(**kwargs) -> dict:
    """Return a test source location."""
    return {
        "location_name": "Source location",
        "source_type": "sonarqube",
        "url": "https://url",
        "landing_url": "",
        "username": "",
        "password": "password",  # nosec
        "private_token": "",
    } | kwargs


def create_report():
    """Return a test report."""
    return {
        "_id": REPORT_ID,
        "report_uuid": REPORT_ID,
        "title": "Report",
        "source_locations": {SOURCE_LOCATION_ID: create_source_location()},
        "subjects": {
            SUBJECT_ID: {
                "name": "Subject",
                "type": "software",
                "metrics": {
                    METRIC_ID: {
                        "name": "Metric",
                        "type": "violations",
                        "target": "0",
                        "accept_debt": False,
                        "tags": ["security"],
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
                "teams_webhook": "",
                "name": "notification_destination",
                "url": "https://reporturl",
            },
        },
        "issue_tracker": {"type": "jira", "parameters": {"username": "jadoe", "password": "secret"}},  # nosec
    }
