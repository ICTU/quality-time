"""Notification."""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, cast

if TYPE_CHECKING:
    from models.destination import Destination
    from models.metric_notification_data import MetricNotificationData
    from models.report import Report


@dataclass
class Notification(ABC):
    """Base class for notifications."""

    report: Report
    metrics: list[MetricNotificationData]
    destination: Destination

    NOTIFICATION_MESSAGE: ClassVar[str] = "subclass responsibility"

    @property
    def report_title(self) -> str:
        """Return the title of the report."""
        return str(self.report["title"])

    @property
    def summary(self) -> str:
        """Return a summary of the notification."""
        nr_changed_metrics = len(self.metrics)
        plural_s = "s" if nr_changed_metrics > 1 else ""
        return f"{self.report_title} has {nr_changed_metrics} metric{plural_s} {self.NOTIFICATION_MESSAGE}"

    @property
    def sorted_metrics(self) -> list[MetricNotificationData]:
        """Return the metrics sorted by name."""
        return sorted(self.metrics, key=lambda metric: metric.metric_name)


@dataclass
class MetricStatusNotification(Notification):
    """Notification of metrics that changed status."""

    NOTIFICATION_MESSAGE: ClassVar[str] = "that changed status"


@dataclass
class TimeLeftNotification(Notification):
    """Notification of metrics that have little time left to be addressed."""

    now: datetime

    NOTIFICATION_MESSAGE: ClassVar[str] = "with a week or less left to address"

    @property
    def sorted_metrics(self) -> list[MetricNotificationData]:
        """Override to return the metrics sorted by deadline, metrics with the least time left first."""
        # Metrics in time left notifications always have a deadline, so the cast is safe:
        return sorted(self.metrics, key=lambda metric: (cast(datetime, metric.deadline), metric.metric_name))
