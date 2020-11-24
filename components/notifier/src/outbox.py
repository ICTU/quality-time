"""Outbox for handling and sending collected notifications."""

from typing import List

from destinations.ms_teams import build_notification_text, send_notification_to_teams
from notification import Notification


def outbox(new_notifications: List[Notification], outbox_contents: List[Notification]):
    """Collect and distribute the generated notifications."""
    outbox_contents = merge_notifications(new_notifications, outbox_contents)
    return send_notifications(outbox_contents)


def merge_notifications(notifications, outbox_contents: List[Notification]) -> List[Notification]:
    """Check if a notification already exists, and if not adds it."""
    for new_notification in notifications:
        is_new = True
        if len(outbox_contents) > 0:
            for old_notification in outbox_contents:
                if new_notification.destination_uuid == old_notification.destination_uuid:
                    old_notification.merge_notification(new_notification.metrics)
                    is_new = False
                    break
        if is_new:
            outbox_contents.append(new_notification)
    return outbox_contents


def send_notifications(metrics_per_configurations: List[Notification]):
    """Send the notifications and remove them from the outbox."""
    for notification in metrics_per_configurations[:]:
        if not notification.not_ready():
            if notification.destination["teams_webhook"]:
                send_notification_to_teams(
                    str(notification.destination["teams_webhook"]),
                    build_notification_text(notification))
                metrics_per_configurations.remove(notification)
    return metrics_per_configurations
