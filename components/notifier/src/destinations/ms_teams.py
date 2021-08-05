"""Microsoft Teams destination."""

import logging

import pymsteams

from models.notification import Notification


def build_notification_text(notification: Notification) -> str:
    """Create and format the contents of the notification."""
    nr_changed = len(notification.metrics)
    plural_s = "s" if nr_changed > 1 else ""
    plural_are = "are" if nr_changed > 1 else "is"
    report_link = f"[{notification.report_title}]({notification.url})"
    result = f"{report_link} has {nr_changed} metric{plural_s} that {plural_are} notable:\n\n"
    for metric_notification_data in notification.metrics:
        name = f"{metric_notification_data.subject_name}: {metric_notification_data.metric_name}"
        new_status = metric_notification_data.new_metric_status
        new_value = (
            "?" if metric_notification_data.new_metric_value is None else metric_notification_data.new_metric_value
        )
        unit = metric_notification_data.metric_unit
        unit = unit if unit.startswith("%") else f" {unit}"
        if metric_notification_data.reason == "status_changed":
            old_value = (
                "?" if metric_notification_data.old_metric_value is None else metric_notification_data.old_metric_value
            )
            result += (
                f"* {name} status is "
                f"{new_status}, was {metric_notification_data.old_metric_status}. "
                f"Value is {new_value}{unit}, was {old_value}{unit}.\n"
            )
        else:
            result += f"* {name} has been {new_status} for three weeks. Value: {new_value}{unit}.\n"
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
