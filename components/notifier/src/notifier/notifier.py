"""Notifier."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import NoReturn

import aiohttp

from destinations.ms_teams import notification_text, send_notification
from strategies.notification_strategy import NotificationFinder


async def notify(
    internal_server_host: str = "localhost", internal_server_port: str = "5002", sleep_duration: int = 60
) -> NoReturn:
    """Notify our users periodically of the number of red metrics."""
    internal_server_api = f"http://{internal_server_host}:{internal_server_port}/api"
    reports_url = f"{internal_server_api}/report"
    measurements_url = f"{internal_server_api}/measurements"
    most_recent_measurement_seen = datetime.max.replace(tzinfo=timezone.utc)
    notification_finder = NotificationFinder()
    while True:
        record_health()
        logging.info("Determining notifications...")
        reports, measurements = await get_reports_and_measurements(reports_url, measurements_url)
        for notification in notification_finder.get_notifications(reports, measurements, most_recent_measurement_seen):
            send_notification(str(notification.destination["webhook"]), notification_text(notification))
        most_recent_measurement_seen = most_recent_measurement_timestamp(measurements)
        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


async def get_reports_and_measurements(reports_url: str, measurements_url: str):
    """Get the reports and measurements from the internal server."""
    async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
        try:
            url = reports_url
            response = await session.get(url)
            reports = (await response.json())["reports"]
            url = measurements_url
            response = await session.get(url)
            measurements = (await response.json())["measurements"]
        except Exception as reason:  # pylint: disable=broad-except
            logging.error("Could not get data from %s: %s", url, reason)
            reports = []
            measurements = []
    return reports, measurements


def record_health() -> None:
    """Record the current date and time in a file to allow for health checks."""
    filename = "/home/notifier/health_check.txt"
    try:
        with open(filename, "w", encoding="utf-8") as health_check:
            health_check.write(datetime.now().isoformat())
    except OSError as reason:
        logging.error("Could not write health check time stamp to %s: %s", filename, reason)


def most_recent_measurement_timestamp(measurements) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=timezone.utc)
    for measurement in measurements:
        most_recent = max(most_recent, datetime.fromisoformat(measurement["end"]))
    return most_recent
