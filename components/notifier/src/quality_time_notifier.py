"""Notifier."""

import asyncio
import logging
import os

import aiohttp
import pymsteams

from strategies.reds_per_report import reds_per_report


async def notify(log_level: int = None) -> None:
    """Notify our users periodically of the number of red metrics."""
    logging.getLogger().setLevel(log_level or logging.ERROR)

    sleep_duration = int(os.environ.get('NOTIFIER_SLEEP_DURATION', 60))
    server_host = os.environ.get('SERVER_HOST', 'localhost')
    server_port = os.environ.get('SERVER_PORT', '5001')
    webhook = os.environ.get('TEAMS_WEBHOOK')

    while True:
        async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
            response = await session.get(f"http://{server_host}:{server_port}/api/v3/reports")
            json = await response.json()

            reds_in_reports = reds_per_report(json)

            notification = "Number of red metrics in each report:"
            for report in reds_in_reports:
                notification += "\n\r - " + report[0] + ": " + str(report[1])

            if webhook:
                logging.info("Sending notification to configured webhook")
                my_teams_message = pymsteams.connectorcard(webhook)
                my_teams_message.text(notification)
                my_teams_message.send()
            else:
                logging.warning("No webhook configured; please set the environment variable TEAMS_WEBHOOK")

            logging.info("Sleeping %.1f seconds...", sleep_duration)
            await asyncio.sleep(sleep_duration)


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
