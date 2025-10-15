"""Notification."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

    @property
    def summary(self) -> str:
        """Return a summary of the notification."""
        nr_changed = len(self.metrics)
        plural_s = "s" if nr_changed > 1 else ""
        return f"{self.report_title} has {nr_changed} metric{plural_s} that changed status"
