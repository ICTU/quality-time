"""Notifier."""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import NoReturn

import aiohttp

from shared_data_model import DATA_MODEL_JSON

from destinations.ms_teams import notification_text, send_notification
from strategies.notification_strategy import NotificationFinder


async def notify(log_level: int = None) -> NoReturn:
    """Notify our users periodically of the number of red metrics."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    sleep_duration = int(os.environ.get("NOTIFIER_SLEEP_DURATION", 60))
    reports_url = (
        f"http://{os.environ.get('INTERNAL_SERVER_HOST', 'localhost')}:"
        f"{os.environ.get('INTERNAL_SERVER_PORT', '5002')}/api/report"
    )
    most_recent_measurement_seen = datetime.max.replace(tzinfo=timezone.utc)
    notification_finder = NotificationFinder(json.loads(DATA_MODEL_JSON))
    while True:
        record_health()
        logging.info("Determining notifications...")
        try:
            async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
                response = await session.get(reports_url)
                reports_json = await response.json()
        except Exception as reason:  # pylint: disable=broad-except
            logging.error("Could not get reports from %s: %s", reports_url, reason)
            reports_json = dict(reports=[])
        for notification in notification_finder.get_notifications(reports_json, most_recent_measurement_seen):
            send_notification(str(notification.destination["webhook"]), notification_text(notification))
        most_recent_measurement_seen = most_recent_measurement_timestamp(reports_json)
        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


def record_health(filename: str = "/home/notifier/health_check.txt") -> None:
    """Record the current date and time in a file to allow for health checks."""
    try:
        with open(filename, "w", encoding="utf-8") as health_check:
            health_check.write(datetime.now().isoformat())
    except OSError as reason:
        logging.error("Could not write health check time stamp to %s: %s", filename, reason)


def most_recent_measurement_timestamp(reports_json) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=timezone.utc)
    for report in reports_json["reports"]:
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if recent_measurements := metric.get("recent_measurements"):
                    most_recent = max(most_recent, datetime.fromisoformat(recent_measurements[-1]["end"]))
    return most_recent


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
