"""Fixtures for tests."""

from shared_test_code.fixtures import METRIC_ID, NOTIFICATION_DESTINATION_ID, REPORT_ID, SUBJECT_ID


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
