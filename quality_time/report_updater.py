"""Report updater."""

import asyncio
import json
import logging
import sys
import time

import aiohttp


async def fetch(api):
    """Fetch one API asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8080/{api}") as response:
            logging.info("Retrieving %s", api)
            return await response.json()


async def fetch_all(apis):
    """Fetch all APIs asynchronously."""
    return await asyncio.gather(*(fetch(api) for api in apis))


def run():
    """Update the reports."""
    logging.getLogger().setLevel(logging.INFO)
    while True:
        with open(sys.argv[1]) as report_config_json_file:
            report_config_json = json.load(report_config_json_file)
        with open(sys.argv[2]) as report_json_file:
            report_json = json.load(report_json_file)
        measurements = list(asyncio.run(fetch_all(report_config_json["metrics"])))
        report_json["measurements"].extend(measurements)
        with open(sys.argv[2], "w") as report_json_file:
            json.dump(report_json, report_json_file, indent="  ")
        time.sleep(10)
