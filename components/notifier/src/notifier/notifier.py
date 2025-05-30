"""Notifier."""

import asyncio
import pathlib
from datetime import UTC, datetime
from os import getenv
from typing import NoReturn

from pymongo.database import Database

from shared.model.measurement import Measurement

from database.reports import get_reports_and_measurements
from destinations.ms_teams import send_notification
from notifier_utilities.log import get_logger
from strategies.notification_strategy import NotificationFinder


async def notify(database: Database, sleep_duration: int = 60) -> NoReturn:
    """Notify our users periodically of the number of red metrics."""
    logger = get_logger()
    most_recent_measurement_seen = datetime.max.replace(tzinfo=UTC)
    notification_finder = NotificationFinder()
    while True:
        record_health()
        logger.info("Determining notifications...")
        try:
            reports, measurements = get_reports_and_measurements(database)
        except Exception:
            logger.exception("Getting reports and measurements failed")
            reports = []
            measurements = []

        for notification in notification_finder.get_notifications(reports, measurements, most_recent_measurement_seen):
            send_notification(str(notification.destination["webhook"]), notification)
        most_recent_measurement_seen = most_recent_measurement_timestamp(measurements)
        logger.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


def record_health() -> None:
    """Record the current date and time in a file to allow for health checks."""
    logger = get_logger()
    filepath = pathlib.Path(getenv("HEALTH_CHECK_FILE", "/home/notifier/health_check.txt"))
    try:
        with filepath.open("w", encoding="utf-8") as health_check:
            health_check.write(datetime.now(tz=UTC).isoformat())
    except OSError:
        logger.exception("Could not write health check time stamp to %s", filepath)


def most_recent_measurement_timestamp(measurements: list[Measurement]) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=UTC)
    for measurement in measurements:
        most_recent = max(most_recent, datetime.fromisoformat(measurement["end"]))
    return most_recent
