"""Notifier."""

import asyncio
import logging
import pathlib
from datetime import UTC, datetime
from os import getenv
from typing import NoReturn

from shared.database.shared_data import get_reports_and_measurements
from shared.model.measurement import Measurement

from destinations.ms_teams import notification_text, send_notification
from strategies.notification_strategy import NotificationFinder


async def notify(sleep_duration: int = 60) -> NoReturn:
    """Notify our users periodically of the number of red metrics."""
    most_recent_measurement_seen = datetime.max.replace(tzinfo=UTC)
    notification_finder = NotificationFinder()
    while True:
        record_health()
        logging.info("Determining notifications...")
        try:
            reports, measurements = get_reports_and_measurements()
        except Exception:
            logging.exception("Getting reports and measurements failed")
            reports = []
            measurements = []

        for notification in notification_finder.get_notifications(reports, measurements, most_recent_measurement_seen):
            send_notification(str(notification.destination["webhook"]), notification_text(notification))
        most_recent_measurement_seen = most_recent_measurement_timestamp(measurements)
        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


def record_health() -> None:
    """Record the current date and time in a file to allow for health checks."""
    filepath = pathlib.Path(getenv("HEALTH_CHECK_FILE", "/home/notifier/health_check.txt"))
    try:
        with filepath.open("w", encoding="utf-8") as health_check:
            health_check.write(datetime.now(tz=UTC).isoformat())
    except OSError:
        logging.exception("Could not write health check time stamp to %s", filepath)


def most_recent_measurement_timestamp(measurements: list[Measurement]) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=UTC)
    for measurement in measurements:
        most_recent = max(most_recent, datetime.fromisoformat(measurement["end"]))
    return most_recent
