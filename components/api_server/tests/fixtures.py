"""Shared test data."""

from typing import cast

from shared.utils.type import MetricId, ReportId, SourceId, SubjectId, NotificationDestinationId


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

JOHN = {"user": "John", "email": "john@example.org", "common_name": "John Doe"}
JENNY = {"user": "Jenny", "email": "jenny@example.org", "common_name": "Jenny Doe"}


def create_report():
    """Return a test report."""
    return {
        "_id": REPORT_ID,
        "report_uuid": REPORT_ID,
        "title": "Report",
        "subjects": {
            SUBJECT_ID: {
                "name": "Subject",
                "type": "software",
                "metrics": {
                    METRIC_ID: {
                        "name": "Metric",
                        "type": "violations",
                        "addition": "sum",
                        "target": "0",
                        "accept_debt": False,
                        "tags": ["security"],
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
                "teams_webhook": "",
                "name": "notification_destination",
                "url": "https://reporturl",
            },
        },
        "issue_tracker": {"type": "jira", "parameters": {"username": "jadoe", "password": "secret"}},
    }
