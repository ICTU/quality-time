"""Microsoft Teams destination."""

from typing import TYPE_CHECKING

import pymsteams

from notifier_utilities.log import get_logger

if TYPE_CHECKING:
    from models.notification import MetricNotificationData, Notification

ICON_URL = "https://raw.githubusercontent.com/ICTU/quality-time/master/resources/icons/%s.png"


def metric_section(metric: MetricNotificationData, report_url: str) -> pymsteams.cardsection:
    """Create a section for a metric status change."""
    section = pymsteams.cardsection()
    section.activityTitle(metric.metric_name)
    section.activitySubtitle(metric.subject_name)
    section.activityImage(ICON_URL % metric.status)
    old_status = metric.old_metric_status
    old_status_text = " (unchanged)" if metric.new_metric_status == old_status else f", was {old_status}"
    section.addFact("Status:", f"{metric.new_metric_status}{old_status_text}")
    unit = metric.metric_unit
    unit_text = unit if (not unit or unit.startswith("%")) else f" {unit}"
    new_value = "unknown" if metric.new_metric_value is None else f"{metric.new_metric_value}{unit_text}"
    old_value = "unknown" if metric.old_metric_value is None else f"{metric.old_metric_value}{unit_text}"
    old_value_text = " (unchanged)" if metric.new_metric_value == metric.old_metric_value else f", was {old_value}"
    section.addFact("Value:", f"{new_value}{old_value_text}")
    section.linkButton("View metric", f"{report_url}#{metric.metric_uuid}")
    return section


def create_connector_card(destination: str, notification: Notification) -> pymsteams.connectorcard:
    """Create a connector card with the notification."""
    card = pymsteams.connectorcard(destination)
    card.title(f"Quality-time notifications for {notification.report_title}")
    card.summary(notification.summary)
    for metric in sorted(notification.metrics, key=lambda metric: metric.metric_name):
        card.addSection(metric_section(metric, notification.report_url))
    return card


def send_notification(destination: str, notification: Notification) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logger = get_logger()
    logger.info("Sending notification to configured teams webhook")
    card = create_connector_card(destination, notification)
    try:
        card.send()
    except Exception:
        logger.exception("Could not deliver notification")
