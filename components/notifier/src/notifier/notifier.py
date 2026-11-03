"""Notifier."""

import asyncio
import pathlib
import tempfile
from datetime import datetime, time, timedelta
from os import getenv
from typing import TYPE_CHECKING, Final, NoReturn

from dateutil.tz import tzlocal, tzutc

from shared.utils.functions import iso_timestamp

from database.reports import get_reports_and_measurements
from destinations.ms_teams import send_notification
from notifier_utilities.log import get_logger
from strategies.notification_strategy import get_metric_status_notifications, get_time_left_notifications

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pymongo.database import Database

    from shared.model.measurement import Measurement

    from models.notification import Notification

# Local times at which to send the time left notifications each day:
TIME_LEFT_NOTIFICATION_TIMES: Final = [time(hour=7, minute=0)]


async def notify(database: Database, sleep_duration: int = 60) -> NoReturn:
    """Notify users of metrics that changed status and of metrics with little time left."""
    logger = get_logger()
    most_recent_measurement_seen = datetime.max.replace(tzinfo=tzutc())
    next_time_left_notification = next_time_left_notification_time(datetime.now(tz=tzlocal()))
    while True:
        record_health()
        logger.info("Determining notifications...")
        try:
            reports, measurements = get_reports_and_measurements(database)
        except Exception:
            logger.exception("Getting reports and measurements failed")
            reports = []
            measurements = []

        await send_notifications(get_metric_status_notifications(reports, measurements, most_recent_measurement_seen))
        most_recent_measurement_seen = most_recent_measurement_timestamp(measurements)
        if (now := datetime.now(tz=tzlocal())) >= next_time_left_notification:
            logger.info("Determining time left notifications...")
            await send_notifications(get_time_left_notifications(reports, measurements, now))
            next_time_left_notification = next_time_left_notification_time(now)
        logger.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


async def send_notifications(notifications: Sequence[Notification]) -> None:
    """Send the notifications to their destinations."""
    for notification in notifications:
        await send_notification(notification.destination.webhook, notification)


def next_time_left_notification_time(now: datetime) -> datetime:
    """Return the first time after now at which to send the time left notifications."""
    next_times = [datetime.combine(now.date(), time_, tzinfo=now.tzinfo) for time_ in TIME_LEFT_NOTIFICATION_TIMES]
    return min(next_time if next_time > now else next_time + timedelta(days=1) for next_time in next_times)


def record_health() -> None:
    """Record the current date and time in a file to allow for health checks."""
    logger = get_logger()
    filepath = pathlib.Path(getenv("HEALTH_CHECK_FILE", pathlib.Path(tempfile.gettempdir()) / "health_check.txt"))
    try:
        with filepath.open("w", encoding="utf-8") as health_check:
            health_check.write(iso_timestamp())
    except OSError:
        logger.exception("Could not write health check time stamp to %s", filepath)


def most_recent_measurement_timestamp(measurements: list[Measurement]) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=tzutc())
    for measurement in measurements:
        most_recent = max(most_recent, datetime.fromisoformat(measurement["end"]))
    return most_recent
