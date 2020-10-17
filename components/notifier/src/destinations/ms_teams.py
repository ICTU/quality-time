"""Microsoft Teams destination."""

import logging
import random

import pymsteams


SALUTATIONS = ("Alas", "Blimey", "Darn", "Oh dear", "Ouch", "Regrettably", "Sadly", "Unfortunately")


def build_notification_text(text_parameters) -> str:
    """Create and format the contents of the notification."""
    nr_red = text_parameters["new_red_metrics"]
    plural_s = "s" if nr_red > 1 else ""
    report_link = f'[{text_parameters["report_title"]}]({text_parameters["url"]})'
    salutation = random.choice(SALUTATIONS)  # nosec, Not used for cryptography
    return f'{salutation}, {report_link} has {nr_red} _new_ red metric{plural_s}.'


def send_notification_to_teams(destination: str, text: str) -> None:
    """Send notification to Microsoft Teams using a Webhook."""
    logging.info("Sending notification to configured webhook")
    my_teams_message = pymsteams.connectorcard(destination)
    my_teams_message.text(text)
    try:
        my_teams_message.send()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Could not deliver notification: %s", reason)
