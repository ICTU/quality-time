"""."""

import os
import logging

from datetime import datetime

from destinations.ms_teams import build_notification_text, send_notification_to_teams

def outbox():
    """."""
    configurations = dict(dict(destination=dict(),
                          previous_notify=datetime.min(),
                          frequency=os.environ.get("NOTIFIER_SLEEP_DURATION"),
                          notifications=dict()))

def update_configurations(configurations, new_configurations):
    """configurations can change."""
    for uuid in new_configurations:
        is_new = True
        for configuration in configurations:
            if uuid == configuration:
                is_new = False
                update_configuration_parameters(configuration, new_configurations[uuid])
                break
        if is_new:
            configurations[uuid] = new_configurations[uuid]
            configurations[uuid]["previous_notify"] = datetime.min()

def update_configuration_parameters(changed_configuration, to_be_updated_configuration):
    """."""
    updated_configuration = to_be_updated_configuration
    for key in changed_configuration:
        updated_configuration[key] = changed_configuration[key]
    return updated_configuration

def add_configuration():
    """."""

def add_notifications(notifications, configurations):
    """."""
    for notification in notifications:
        for configuration in configurations:
            if notification == configuration:
                configuration[notification] = ""

def send_notifications(configurations):
    """."""
    for configuration in configurations:
        if configuration["destination"]["teams_webhook"]:
            send_notification_to_teams(
                str(configuration["destination"]["teams_webhook"]), build_notification_text(configuration["notifications"]))
            configuration["previous_notify"] = datetime.now()
            remove_send_notifications(configuration)

def remove_send_notifications(configuration):
    configuration["notifications"] = dict()
