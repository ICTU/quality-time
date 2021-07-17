"""Notifier."""

import asyncio
import logging
import os
import traceback
from datetime import datetime, timezone
from typing import Final, NoReturn, cast

import aiohttp

from notifier_utilities.type import JSON, URL
from outbox import Outbox
from strategies.notification_strategy import NotificationFinder


async def notify(log_level: int = None) -> NoReturn:
    """Notify our users periodically of the number of red metrics."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    sleep_duration = int(os.environ.get("NOTIFIER_SLEEP_DURATION", 60))
    api_version = "v3"
    reports_url = (
        f"http://{os.environ.get('SERVER_HOST', 'localhost')}:"
        f"{os.environ.get('SERVER_PORT', '5001')}/api/{api_version}/report"
    )
    data_model = await retrieve_data_model(api_version)
    most_recent_measurement_seen = datetime.max.replace(tzinfo=timezone.utc)
    outbox = Outbox()
    notification_finder = NotificationFinder(data_model)
    while True:
        record_health()
        logging.info("Determining notifications...")
        try:
            async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
                response = await session.get(reports_url)
                json = await response.json()
        except Exception as reason:  # pylint: disable=broad-except
            logging.error("Could not get reports from %s: %s", reports_url, reason)
            json = dict(reports=[])
        notifications = notification_finder.get_notifications(json, most_recent_measurement_seen)
        outbox.add_notifications(notifications)
        outbox.send_notifications()
        most_recent_measurement_seen = most_recent_measurement_timestamp(json)
        logging.info("Sleeping %.1f seconds...", sleep_duration)
        await asyncio.sleep(sleep_duration)


async def retrieve_data_model(api_version: str) -> JSON:
    """Retrieve data model from server."""
    max_sleep_duration = 60  # Make an environment variable
    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(raise_for_status=True, timeout=timeout, trust_env=True) as session:
        data_model = await fetch_data_model(session, max_sleep_duration, api_version)
    return data_model


def record_health(filename: str = "/home/notifier/health_check.txt") -> None:
    """Record the current date and time in a file to allow for health checks."""
    try:
        with open(filename, "w") as health_check:
            health_check.write(datetime.now().isoformat())
    except OSError as reason:
        logging.error("Could not write health check time stamp to %s: %s", filename, reason)


def most_recent_measurement_timestamp(json) -> datetime:
    """Return the most recent measurement timestamp."""
    most_recent = datetime.min.replace(tzinfo=timezone.utc)
    for report in json["reports"]:
        for subject in report["subjects"].values():
            for metric in subject["metrics"].values():
                if recent_measurements := metric.get("recent_measurements"):
                    most_recent = max(most_recent, datetime.fromisoformat(recent_measurements[-1]["end"]))
    return most_recent


async def fetch_data_model(session: aiohttp.ClientSession, sleep_duration: int, api_version: str) -> JSON:
    """Fetch the data model."""
    # The first attempt is likely to fail because the collector starts up faster than the server,
    # so don't log tracebacks on the first attempt
    server_url: Final[URL] = URL(
        f"http://{os.environ.get('SERVER_HOST', 'localhost')}:{os.environ.get('SERVER_PORT', '5001')}"
    )

    first_attempt = True
    data_model_url = URL(f"{server_url}/api/{api_version}/datamodel")
    while True:
        record_health()
        logging.info("Loading data model from %s...", data_model_url)
        if data_model := await get_data_from_api(session, data_model_url, log=not first_attempt):
            return data_model
        first_attempt = False
        logging.warning("Loading data model failed, trying again in %ss...", sleep_duration)
        await asyncio.sleep(sleep_duration)


async def get_data_from_api(session: aiohttp.ClientSession, api: URL, log: bool = True) -> JSON:
    """Get data from the API url."""
    try:
        response = await session.get(api)
        json = cast(JSON, await response.json())
        response.close()
        return json
    except Exception as reason:  # pylint: disable=broad-except
        if log:
            logging.error("Getting data from %s failed: %s", api, reason)
            logging.error(traceback.format_exc())
        return {}


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
