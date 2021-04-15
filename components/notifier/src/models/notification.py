"""Notification."""

from models.metric_notification_data import MetricNotificationData


class Notification:
    """Handle notification contents and status."""

    def __init__(self, report, metrics, destination_uuid, destination):
        """Initialise the Notification with the required info."""
        self.report_title = report["title"]
        self.url = report.get("url")
        self.metrics: list[MetricNotificationData] = metrics
        self.destination_uuid = destination_uuid
        self.destination = destination

    def __eq__(self, other):
        """Check if the notification itself is the same, regardless of its metric content."""
        return (
            self.report_title == other.report_title
            and self.destination_uuid == other.destination_uuid
            and self.destination == other.destination
        )

    def merge_notification(self, new_metrics):
        """Merge new metrics into this notification."""
        self.metrics.extend(new_metrics)
