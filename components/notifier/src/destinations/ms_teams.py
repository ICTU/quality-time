"""Microsoft Teams destination."""

import logging

import pymsteams


def send_notification_to_teams(destination, text):
    """Send notification to Microsoft teams using a Webhook."""
    if not destination:
        logging.warning("No webhook configured")
        return False
    if not text:
        logging.error("No text passed to send as notification; please fix this bug")
        return False

    logging.info("Sending notification to configured webhook")
    my_teams_message = pymsteams.connectorcard(destination)
    my_teams_message.text(text)
    try:
        my_teams_message.send()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Could not deliver notification: %s", reason)
        return False
    return True
