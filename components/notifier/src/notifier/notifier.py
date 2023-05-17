"""Notifier."""

import asyncio
import logging
from datetime import datetime, timezone, UTC
from os import getenv
from typing import NoReturn

from destinations.ms_teams import notification_text, send_notification
from notifier_utilities.data import get_reports_and_measurements
from strategies.notification_strategy import NotificationFinder


async def notify(sleep_duration: int = 60) -> NoReturn:
    """Notify our users periodically of the number of red metrics."""
    most_recent_measurement_seen = datetime.max.replace(tzinfo=timezone.utc)
    notification_finder = NotificationFinder()
    while True:
        record_health()
        logging.info("Determining notifications...")
        try:
            reports, measurements = get_reports_and_measurements()
        except Exception as reason:  # pylint: disable=broad-except
            logging.error("Getting reports and measurements failed: %s", reason)
            reports = []
            measurements = []

        for notification in notification_finder.get_notifications(reports, measurements, most_recent_measurement_seen):
            send_notification(str(notification.destination["webhook"]), notification_text(notification))
        most_recent_measurement_seen = most_recent_measurement_timestamp(measurements)
        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


def record_health() -> None:
    """Record the current date and time in a file to allow for health checks."""
    filename = getenv("HEALTH_CHECK_FILE", "/home/notifier/health_check.txt")
    try:
        with open(filename, "w", encoding="utf-8") as health_check:
            health_check.write(datetime.now(tz=UTC).isoformat())
    except OSError as reason:
        logging.error("Could not write health check time stamp to %s: %s", filename, reason)


def most_recent_measurement_timestamp(measurements) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=timezone.utc)
    for measurement in measurements:
        most_recent = max(most_recent, datetime.fromisoformat(measurement["end"]))
    return most_recent
