"""Shared test data."""

from shared_test_code.fixtures import METRIC_ID, NOTIFICATION_DESTINATION_ID, REPORT_ID, SOURCE_ID, SUBJECT_ID

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
                        "target": "0",
                        "accept_debt": False,
                        "tags": ["security"],
                        "scales": ["count", "percentage"],
                        "sources": {
                            SOURCE_ID: {
                                "type": "sonarqube",
                                "name": "Source",
                                "parameters": {"url": "https://url", "password": "password", "tags": ["security"]},  # nosec
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
