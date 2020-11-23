"""."""

import os
import logging

from datetime import datetime

from destinations.ms_teams import build_notification_text, send_notification_to_teams

def outbox(notable_metrics, outbox_contents, sleep_duration):
    """Method pattern for distributing notifications at the appropriate time."""
    outbox_configurations = add_configurations(notable_metrics["notification_destinations"], outbox_contents, sleep_duration)
    add_notifications(notable_metrics["metrics"], outbox_configurations)
    return send_notification_to_teams()

# def update_configuration_parameters(changed_configuration, to_be_updated_configuration):
#     """."""
#     updated_configuration = to_be_updated_configuration
#     for key in changed_configuration:
#         updated_configuration[key] = changed_configuration[key]
#     return updated_configuration

def add_configurations(new_configurations, sleep_duration, existing_configurations):
    """Check if a configuration already exists, and if not adds it."""
    for new in new_configurations:
        is_new = True
        if len(existing_configurations) > 0:
            for configuration_uuid in existing_configurations:
                if new in configuration_uuid:
                    is_new = False
                    break
        if is_new:
            existing_configurations[new] = dict(
                destination=new,
                previous_notify=datetime.now() - sleep_duration,
                notifications=dict()
            )
    return existing_configurations

def add_notifications(new_notifications, configurations):
    """Add notifications to the configurations."""
    for configuration_uuid in configurations:
        for new_notification_uuid in new_notifications:
            if new_notification_uuid in configuration_uuid:
                configuration_uuid[new_notification_uuid] = dict(
                    metric_type="",
                    metric_name="",
                    metric_unit="",
                    new_metric_status="",
                    new_metric_value="",
                    old_metric_status="",
                    old_metric_value=""
                )

def send_notifications(metrics_per_configurations):
    """Send the notifications and remove them from the outbox."""
    for configuration in metrics_per_configurations:
        if datetime.now() - configuration["destination"]["previous_notify"] > configuration["destination"]["interval"]:
            if configuration["destination"]["teams_webhook"]:
                send_notification_to_teams(
                    str(configuration["destination"]["teams_webhook"]),
                    build_notification_text(configuration["notifications"]))
                configuration["previous_notify"] = datetime.now()
                del metrics_per_configurations[configuration]
    return metrics_per_configurations
