"""Microsoft Teams destination."""

import logging
import random

import pymsteams


SALUTATIONS = ("Alas", "Blimey", "Darn", "Oh dear", "Ouch", "Regrettably", "Sadly", "Unfortunately")


def get_status(status, data_model) -> str:
    """"get the user friendly status name"""
    statuses = data_model["sources"]["quality_time"]["parameters"]["status"]["api_values"]
    for user_friendly_status in statuses:
        if statuses[user_friendly_status] == status:
            return user_friendly_status
    return "Unknown status"


def build_notification_text(text_parameters, data_model) -> str:
    """Create and format the contents of the notification."""
    nr_red = text_parameters["new_red_metrics"]
    plural_s = "s" if nr_red > 1 else ""
    report_link = f'[{text_parameters["report_title"]}]({text_parameters["url"]})'
    salutation = random.choice(SALUTATIONS)  # nosec, Not used for cryptography

    result = f'{salutation}, {report_link} has {nr_red} metric{plural_s} that turned red.'
    for metric in text_parameters["metrics"]:
        name = f'{data_model["metrics"][metric["metric_type"]]["name"]}'
        old_status = f'{get_status(metric["old_metric_status"], data_model)}'
        new_status = f'{get_status(metric["new_metric_status"], data_model)}'
        unit = f'{data_model["metrics"][metric["metric_type"]]["unit"]}'

        result += f'<br> {name} status is {new_status}, was {old_status}. ' \
                  f'Value is {metric["new_metric_value"]}{unit} was {metric["old_metric_value"]}{unit}.'
    return result


def build_notification_detailed_text_partial(text_parameters) -> str:
    """Create and format the contents of the notification."""
    nr_red = text_parameters["new_red_metrics"]
    plural_s = "s" if nr_red > 1 else ""
    report_link = f'[{text_parameters["report_title"]}]({text_parameters["url"]})'
    salutation = random.choice(SALUTATIONS)  # nosec, Not used for cryptography
    return f'{salutation}, {report_link} has {nr_red} metric{plural_s} that turned red.'


def send_notification_to_teams(destination: str, text: str) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logging.info("Sending notification to configured webhook")
    my_teams_message = pymsteams.connectorcard(destination)
    my_teams_message.text(text)
    try:
        my_teams_message.send()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Could not deliver notification: %s", reason)
