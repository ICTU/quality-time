"""Microsoft Teams destination."""

import logging

import pymsteams

from models.notification import MetricNotificationData, Notification


def notification_text(notification: Notification) -> str:
    """Create and format the contents of the notification."""
    nr_changed = len(notification.metrics)
    plural_s = "s" if nr_changed > 1 else ""
    markdown = f"{notification.report_title} has {nr_changed} metric{plural_s} that changed status:\n\n"
    for subject_name in sorted({metric.subject_name for metric in notification.metrics}):
        markdown += _subject_notification_text(notification, subject_name)
    return markdown


def _subject_notification_text(notification: Notification, subject_name: str) -> str:
    """Return the notification text for the subject."""
    markdown = f"* {subject_name}:\n"
    subject_metrics = [metric for metric in notification.metrics if metric.subject_name == subject_name]
    for metric in sorted(subject_metrics, key=lambda metric: metric.metric_name):
        markdown += _metric_notification_text(metric)
    return markdown


def _metric_notification_text(metric: MetricNotificationData) -> str:
    """Return the notification text for the metric."""
    new_value = "?" if metric.new_metric_value is None else metric.new_metric_value
    old_value = "?" if metric.old_metric_value is None else metric.old_metric_value
    unit = metric.metric_unit if metric.metric_unit.startswith("%") else f" {metric.metric_unit}"
    old_value_text = " (unchanged)" if new_value == old_value else f", was {old_value}{unit}"
    return (
        f"  * *{metric.metric_name}* status is {metric.new_metric_status}, was {metric.old_metric_status}. "
        f"Value is {new_value}{unit}{old_value_text}.\n"
    )


def send_notification(destination: str, notification: Notification) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logging.info("Sending notification to configured teams webhook")
    teams_message = pymsteams.connectorcard(destination)
    teams_message.title("Quality-time notification")
    teams_message.addLinkButton(f"Open the '{notification.report_title}' report", notification.report_url)
    teams_message.text(notification_text(notification))
    try:
        teams_message.send()
    except Exception:
        logging.exception("Could not deliver notification")
