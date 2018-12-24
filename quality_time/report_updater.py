"""Report updater."""

import asyncio
import datetime
import json
import logging
import time

import aiohttp
import dataset

from .util import hash_request_url


async def fetch(session, api):
    """Fetch one API asynchronously."""
    async with session.get(f"http://localhost:8080/{api}") as response:
        logging.info("Retrieving %s", api)
        return await response.json()


async def fetch_and_store_measurement(session, api):
    """Fetch and store one measurement."""
    measurement = await fetch(session, api)
    column = hash_request_url(measurement["request"]["request_url"])
    timestamp = datetime.datetime.fromisoformat(measurement["measurement"]["timestamp"])
    with dataset.connect("sqlite:///measurements.db") as database:
        database[column].insert(dict(timestamp=timestamp, measurement=json.dumps(measurement)))


async def fetch_report_and_measurements():
    """Fetch the report and its measurements."""
    async with aiohttp.ClientSession() as session:
        report_config_json = await fetch(session, "report")
        metrics = []
        for subject in report_config_json["subjects"]:
            metrics.extend(subject["metrics"])
        await asyncio.gather(*(fetch_and_store_measurement(session, api) for api in metrics))


def run():
    """Update the reports."""
    logging.getLogger().setLevel(logging.INFO)

    while True:
        asyncio.run(fetch_report_and_measurements())
        logging.info("Starting sleep...")
        time.sleep(10)
