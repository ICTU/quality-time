"""Notifier."""

import asyncio
import logging
import os

import aiohttp

from destinations.ms_teams import send_notification_to_teams
from strategies.reds_that_are_new import reds_that_are_new


async def notify(log_level: int = None) -> None:
    """Notify our users periodically of the number of red metrics."""
    logging.getLogger().setLevel(log_level or logging.ERROR)

    sleep_duration = int(os.environ.get('NOTIFIER_SLEEP_DURATION', 60))
    server_host = os.environ.get('SERVER_HOST', 'localhost')
    server_port = os.environ.get('SERVER_PORT', '5001')

    while True:
        async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
            response = await session.get(f"http://{server_host}:{server_port}/api/v3/reports")
            json = await response.json()

        notifications = reds_that_are_new(json)

        total_new_red_metrics = sum(notification["new_red_metrics"] for notification in notifications)
        if total_new_red_metrics > 0:
            for notification in notifications:
                text = build_notification_text(notifications)
                send = send_notification_to_teams(notification["teams_webhook"], text)
                if not send:
                    logging.warning("unable to send the notification for %s", notification["report_uuid"])
        else:
            logging.info("no new red metrics")

        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


def build_notification_text(text_parameters):
    """Create and format the contents of the notification."""
    text = "number of <i>new</i> red metrics in each report:"
    for notification in text_parameters:
        text += f'\n\r[{notification["report_title"]}]({notification["url"]}):' \
                f' {notification["new_red_metrics"]}'
    return text


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
