"""Outbox for handling and sending collected notifications."""

import os
from typing import List

from destinations.ms_teams import build_notification_text, send_notification_to_teams
from notification import Notification


def outbox(new_notifications: List[Notification], outbox_contents: List[Notification]):
    """Collect and distribute the generated notifications."""
    outbox_contents = merge_notifications(new_notifications, outbox_contents)
    return send_notifications(outbox_contents)

# def update_configuration_parameters(changed_configuration, to_be_updated_configuration):
#     """."""
#     updated_configuration = to_be_updated_configuration
#     for key in changed_configuration:
#         updated_configuration[key] = changed_configuration[key]
#     return updated_configuration


def merge_notifications(notifications, outbox_contents: List[Notification]) -> List[Notification]:
    """Check if a notification already exists, and if not adds it."""
    sleep_duration = int(os.environ.get('NOTIFIER_SLEEP_DURATION', 60))
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

        # if datetime.now() - notification["destination"]["previous_notify"] > notification["destination"]["interval"]:
        #     if notification["destination"]["teams_webhook"]:
        #         send_notification_to_teams(
        #             str(notification["destination"]["teams_webhook"]),
        #             build_notification_text(notification["notifications"]))
        #         notification["previous_notify"] = datetime.now()
        #         del metrics_per_configurations[notification]
