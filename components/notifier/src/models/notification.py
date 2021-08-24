"""Notification."""

from dataclasses import dataclass
from typing import Optional

from notifier_utilities.type import JSON
from models.metric_notification_data import MetricNotificationData


@dataclass
class Notification:
    """Handle notification contents and status."""

    report: JSON
    metrics: list[MetricNotificationData]
    destination_uuid: str
    destination: dict[str, str]

    @property
    def report_title(self) -> str:
        """Return the title of the report."""
        return str(self.report["title"])

    @property
    def url(self) -> Optional[str]:
        """Return the URL of the report."""
        return self.report.get("url")
