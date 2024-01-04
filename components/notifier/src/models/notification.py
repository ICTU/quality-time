"""Notification."""

from dataclasses import dataclass

from models.metric_notification_data import MetricNotificationData
from notifier_utilities.type import JSON


@dataclass
class Notification:
    """Handle notification contents and status."""

    report: JSON
    report_url: str  # The landing URL to be included in the notification so users can navigate back to Quality-time
    metrics: list[MetricNotificationData]
    destination: dict[str, str]

    @property
    def report_title(self) -> str:
        """Return the title of the report."""
        return str(self.report["title"])
