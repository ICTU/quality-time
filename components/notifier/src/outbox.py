"""Outbox for handling and sending collected notifications."""

from destinations.ms_teams import build_notification_text, send_notification
from models.notification import Notification


class Outbox:
    """Handle storing and sending notifications."""

    def __init__(self, notifications: list[Notification] = None) -> None:
        """Initialise the Notification with the required info."""
        self.notifications = notifications or []

    def add_notifications(self, notifications: list[Notification]):
        """Check if a notification is already in the outbox, and if not, add it."""
        merged = False
        for new_notification in notifications:
            for old_notification in self.notifications:
                if new_notification == old_notification:
                    old_notification.merge_notification(new_notification.metrics)
                    merged = True
                    break
            if not merged:
                self.notifications.append(new_notification)
                merged = False

    def send_notifications(self) -> int:
        """Send the notifications that are ready to be sent, remove them from the outbox."""
        nr_sent = 0
        for notification in self.notifications[:]:
            if notification.destination["webhook"]:
                send_notification(str(notification.destination["webhook"]), build_notification_text(notification))
                nr_sent += 1
                self.notifications.remove(notification)
        return nr_sent
