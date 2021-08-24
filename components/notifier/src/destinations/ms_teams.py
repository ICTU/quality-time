"""Microsoft Teams destination."""

import logging

import pymsteams

from models.notification import Notification


def build_notification_text(notification: Notification) -> str:
    """Create and format the contents of the notification."""
    nr_changed = len(notification.metrics)
    plural_s = "s" if nr_changed > 1 else ""
    report_link = f"[{notification.report_title}]({notification.url})"
    result = f"{report_link} has {nr_changed} metric{plural_s} that changed status:\n\n"
    subjects = sorted(list(set(metric.subject_name for metric in notification.metrics)))
    for subject in subjects:
        result += f"* {subject}:\n"
        for metric in [m for m in notification.metrics if m.subject_name == subject]:
            new_value = "?" if metric.new_metric_value is None else metric.new_metric_value
            old_value = "?" if metric.old_metric_value is None else metric.old_metric_value
            unit = metric.metric_unit if metric.metric_unit.startswith("%") else f" {metric.metric_unit}"
            old_value_text = " (unchanged)" if new_value == old_value else f", was {old_value}{unit}"
            result += (
                f"  * *{metric.metric_name}* status is {metric.new_metric_status}, was {metric.old_metric_status}. "
                f"Value is {new_value}{unit}{old_value_text}.\n"
            )
    return result


def send_notification(destination: str, text: str) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logging.info("Sending notification to configured teams webhook")
    my_teams_message = pymsteams.connectorcard(destination)
    my_teams_message.text(text)
    try:
        my_teams_message.send()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Could not deliver notification: %s", reason)
