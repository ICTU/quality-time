"""Outbox for handling and sending collected notifications."""

from typing import List

from destinations.ms_teams import build_notification_text, send_notification_to_teams
from notification import Notification


def outbox(new_notifications: List[Notification], outbox_contents: List[Notification]):
    """Collect and distribute the generated notifications."""
    outbox_contents = merge_notifications(new_notifications, outbox_contents)
    return send_notifications(outbox_contents)


def merge_notifications(outbox: List[Notification], notifications: List[Notification]) -> List[Notification]:
    """Check if a notification already exists, and if not, add it to the outbox."""
    for new_notification in notifications:
        for old_notification in outbox:
            if new_notification.destination_uuid == old_notification.destination_uuid:
                old_notification.merge_notification(new_notification.metrics)
                break
        else:
            outbox.append(new_notification)
    return outbox


def send_notifications(notifications: List[Notification]):
    """Send the notifications that are ready to be sent and remove them from the outbox."""
    for notification in notifications[:]:
        if notification.ready() and notification.destination["teams_webhook"]:
            send_notification_to_teams(
                str(notification.destination["teams_webhook"]), build_notification_text(notification)
            )
            notifications.remove(notification)
    return notifications
