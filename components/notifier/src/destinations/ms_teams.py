"""Microsoft Teams destination."""

import logging

import pymsteams


def build_notification_text(text_parameters) -> str:
    """Create and format the contents of the notification."""
    nr_changed = len(text_parameters["metrics"])
    plural_s = "s" if nr_changed > 1 else ""
    report_link = f'[{text_parameters["report_title"]}]({text_parameters["url"]})'

    result = f'{report_link} has {nr_changed} metric{plural_s} that changed status:\n\n'
    for metric in text_parameters["metrics"]:
        name = metric["metric_name"]
        unit = metric["metric_unit"]
        unit = unit if unit.startswith("%") else f" {unit}"
        new_value = '?' if metric["new_metric_value"] is None else metric["new_metric_value"]
        old_value = '?' if metric["old_metric_value"] is None else metric["old_metric_value"]
        result += f'* {name} status is {metric["new_metric_status"]}, was {metric["old_metric_status"]}. ' \
                  f'Value is {new_value}{unit}, was {old_value}{unit}.\n'
    return result


def send_notification_to_teams(destination: str, text: str) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logging.info("Sending notification to configured webhook")
    my_teams_message = pymsteams.connectorcard(destination)
    my_teams_message.text(text)
    try:
        my_teams_message.send()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Could not deliver notification: %s", reason)
