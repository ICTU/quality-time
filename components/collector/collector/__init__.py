"""Measurement collector."""

import logging
import os
import urllib.parse
from time import sleep
from typing import cast, Dict, Type

import requests

# Make sure subclasses are registered
from .collectors import *  # pylint: disable=unused-wildcard-import,wildcard-import
from .collector import collect_measurement
from .type import URL


def get(api: URL) -> Dict:
    """Get data from the API url."""
    try:
        return requests.get(api).json()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Getting data from %s failed: %s", api, reason)
        return {}


def post(api: URL, data) -> None:
    """Post the JSON data to the api url."""
    try:
        requests.post(api, json=data)
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Posting %s to %s failed: %s", data, api, reason)


def fetch_measurements(server: URL) -> None:
    """Fetch the metrics and their measurements."""
    metrics = get(URL(f"{server}/metrics"))
    for metric_uuid, metric in metrics.items():
        measurement = collect_measurement(metric)
        measurement["metric_uuid"] = metric_uuid
        measurement["report_uuid"] = metric["report_uuid"]
        post(URL(f"{server}/measurements"), measurement)


def collect() -> None:
    """Collect the measurements indefinitively."""
    logging.getLogger().setLevel(logging.INFO)

    while True:
        logging.info("Collecting...")
        fetch_measurements(URL(os.environ.get("SERVER_URL", "http://localhost:8080")))
        logging.info("Sleeping...")
        sleep(60)


if __name__ == "__main__":
    collect()  # pragma: nocover
