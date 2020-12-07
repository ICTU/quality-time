"""Outbox for handling and sending collected notifications."""

from typing import List

from destinations.ms_teams import build_notification_text, send_notification_to_teams
from notification import Notification


def process_outbox(outbox: List[Notification], new_notifications: List[Notification]):
    """Collect and distribute the generated notifications."""
    outbox = merge_notifications(outbox, new_notifications)
    return send_notifications(outbox)


def merge_notifications(outbox: List[Notification], notifications: List[Notification]) -> List[Notification]:
    """Check if a notification already exists, and if not, add it to the outbox."""
    merged = False
    for new_notification in notifications:
        for old_notification in outbox:
            if new_notification == old_notification:
                old_notification.merge_notification(new_notification.metrics)
                merged = True
                break
        if not merged:
            outbox.append(new_notification)
            merged = False
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
