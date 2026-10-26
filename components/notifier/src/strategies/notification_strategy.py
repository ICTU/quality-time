"""Strategies for notifying users about metrics."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Final

from models.metric_notification_data import MetricNotificationData
from models.notification import MetricStatusNotification, TimeLeftNotification
from notifier_utilities.log import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator

    from shared.model.measurement import Measurement
    from shared.utils.type import MetricId

    from models.destination import Destination
    from models.report import Report

TIME_LEFT_WINDOW: Final = timedelta(weeks=1)  # Notify of metrics with this amount of time or less left to address them


def get_metric_status_notifications(
    reports: list[Report],
    measurements: list[Measurement],
    most_recent_measurement_seen: datetime,
) -> list[MetricStatusNotification]:
    """Return the notifications for the metrics that changed status."""
    notifications: list[MetricStatusNotification] = []
    for report, destinations, metrics in _notification_data_per_report(reports, measurements):
        if changed_metrics := [
            metric for metric in metrics if metric.status_changed_after(most_recent_measurement_seen)
        ]:
            notifications.extend(
                MetricStatusNotification(report, changed_metrics, destination) for destination in destinations
            )
    return notifications


def get_time_left_notifications(
    reports: list[Report],
    measurements: list[Measurement],
    now: datetime,
) -> list[TimeLeftNotification]:
    """Return the notifications for the metrics that have little time left."""
    notifications: list[TimeLeftNotification] = []
    for report, destinations, metrics in _notification_data_per_report(reports, measurements):
        if urgent_metrics := [metric for metric in metrics if metric.deadline_on_or_before(now + TIME_LEFT_WINDOW)]:
            notifications.extend(
                TimeLeftNotification(report, urgent_metrics, destination, now) for destination in destinations
            )
    return notifications


def _notification_data_per_report(
    reports: list[Report], measurements: list[Measurement]
) -> Iterator[tuple[Report, list[Destination], list[MetricNotificationData]]]:
    """Yield the reports with notification destinations, together with the destinations and their metrics."""
    measurements_by_metric = _measurements_per_metric(measurements)
    for report in reports:
        if destinations := report.destinations():
            yield report, destinations, _notification_data(report, measurements_by_metric)


def _measurements_per_metric(measurements: list[Measurement]) -> dict[MetricId, list[Measurement]]:
    """Return the measurements per metric, sorted ascending by end timestamp."""
    measurements_per_metric: dict[MetricId, list[Measurement]] = defaultdict(list)
    for measurement in sorted(measurements, key=lambda measurement: str(measurement["end"])):
        measurements_per_metric[measurement["metric_uuid"]].append(measurement)
    return measurements_per_metric


def _notification_data(
    report: Report, measurements_by_metric: dict[MetricId, list[Measurement]]
) -> list[MetricNotificationData]:
    """Return the notification data of the metrics of the report, skipping metrics whose data can't be determined."""
    logger = get_logger()
    notification_data = []
    for subject in report["subjects"].values():
        for metric_uuid, metric in subject["metrics"].items():
            metric_measurements = measurements_by_metric.get(metric_uuid, [])
            try:
                notification_data.append(MetricNotificationData(metric, metric_uuid, metric_measurements, subject))
            except Exception:
                logger.exception("Skipping metric %s because determining its notification data failed", metric_uuid)
    return notification_data
