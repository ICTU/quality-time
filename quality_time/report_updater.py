"""Report updater."""

import asyncio
import json
import logging
import os
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
    if not os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'w') as report_json_file:
            json.dump(dict(measurements=[]), report_json_file, indent="  ")

    while True:
        report_config_json = asyncio.run(fetch("report"))
        with open(sys.argv[1]) as report_json_file:
            report_json = json.load(report_json_file)
        metrics = []
        for subject in report_config_json["subjects"]:
            metrics.extend(subject["metrics"])
        measurements = list(asyncio.run(fetch_all(metrics)))
        report_json["measurements"].extend(measurements)
        with open(sys.argv[1], "w") as report_json_file:
            json.dump(report_json, report_json_file, indent="  ")
        time.sleep(10)
