"""Measurement collector."""

import logging
import os
import urllib.parse
import time
from typing import cast, Dict, NoReturn, Type

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


class Fetcher:
    """Fetch measurements."""
    def __init__(self):
        self.server_url = URL(os.environ.get("SERVER_URL", "http://localhost:8080"))
        self.last_fetch = dict()

    def start(self) -> NoReturn:
        """Start fetching measurements indefinitely."""
        while True:
            logging.info("Collecting...")
            self.fetch_measurements()
            logging.info("Sleeping...")
            time.sleep(60)

    def fetch_measurements(self) -> None:
        """Fetch the metrics and their measurements."""
        metrics = get(URL(f"{self.server_url}/metrics"))
        for metric_uuid, metric in metrics.items():
            measurement = collect_measurement(metric)
            measurement["metric_uuid"] = metric_uuid
            measurement["report_uuid"] = metric["report_uuid"]
            post(URL(f"{self.server_url}/measurements"), measurement)


def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(logging.INFO)
    Fetcher().start()


if __name__ == "__main__":
    collect() # pragma: nocover
