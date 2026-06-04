"""Shared test data."""

from typing import TYPE_CHECKING

from shared_test_code.fixtures import METRIC_ID, NOTIFICATION_DESTINATION_ID, SOURCE_ID, SUBJECT_ID

if TYPE_CHECKING:
    from shared.utils.type import MetricId


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
                                "parameters": {"url": "https://url", "password": "password"},  # nosec
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
