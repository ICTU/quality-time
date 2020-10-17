"""Notifier."""

import asyncio
import datetime
import logging
import os

import aiohttp

from destinations.ms_teams import build_notification_text, send_notification_to_teams
from strategies.reds_that_are_new import reds_that_are_new


async def notify(log_level: int = None) -> None:
    """Notify our users periodically of the number of red metrics."""
    logging.getLogger().setLevel(log_level or logging.ERROR)

    sleep_duration = int(os.environ.get('NOTIFIER_SLEEP_DURATION', 60))
    server_host = os.environ.get('SERVER_HOST', 'localhost')
    server_port = os.environ.get('SERVER_PORT', '5001')
    reports_url = f"http://{server_host}:{server_port}/api/v3/reports"
    most_recent_measurement_seen = datetime.datetime.max.isoformat()

    while True:
        logging.info("Determining notifications...")
        try:
            async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
                response = await session.get(reports_url)
                json = await response.json()
        except Exception as reason:  # pylint: disable=broad-except
            logging.error("Could not get reports from %s: %s", reports_url, reason)
            json = dict(reports=[])

        notifications = reds_that_are_new(json, most_recent_measurement_seen)
        for notification in notifications:
            destination = str(notification["teams_webhook"])
            text = build_notification_text(notification)
            send_notification_to_teams(destination, text)

        most_recent_measurement_seen = most_recent_measurement_timestamp(json)
        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


def most_recent_measurement_timestamp(json) -> str:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.datetime.min.isoformat()
    for report in json["reports"]:
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if recent_measurements := metric.get("recent_measurements"):
                    most_recent = max(most_recent, recent_measurements[-1]["end"])
    return most_recent


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
