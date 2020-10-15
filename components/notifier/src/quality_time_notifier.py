"""Notifier."""

import asyncio
import logging
import os

import aiohttp

from destinations.ms_teams import send_notification_to_teams
from strategies.reds_per_report import reds_per_report


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

        notifications = reds_per_report(json)

        for notification in notifications:
            text = "\n\r" + notification["report_name"] + " contains " + str(notification["red_metrics"]) + \
                   " red metrics" + "\n\r" + notification["url"]
            send = send_notification_to_teams(notification["teams_webhook"], text)
            if not send:
                logging.warning("unable to send the notification for %s", notification["report_name"])

        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
