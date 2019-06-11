"""Measurement collector."""

from datetime import datetime, timedelta
import logging
import os
import urllib.parse
import time
from typing import Any, cast, Dict, NoReturn, Type

import requests

# Make sure subclasses are registered
from .collectors import *  # pylint: disable=unused-wildcard-import,wildcard-import
from .collector import MetricCollector
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


class MetricsCollector:
    """Collect measurements for all metrics."""
    def __init__(self) -> None:
        self.server_url = URL(os.environ.get("SERVER_URL", "http://localhost:8080"))
        self.next_fetch: Dict[str, datetime] = dict()
        self.last_parameters: Dict[str, Any] = dict()

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
            collector = MetricCollector(metric)
            if not collector.can_collect():
                continue
            if self.skip(metric_uuid, metric):
                continue
            measurement = collector.get()
            self.last_parameters[metric_uuid] = metric
            self.next_fetch[metric_uuid] = collector.next_collection()
            measurement["metric_uuid"] = metric_uuid
            measurement["report_uuid"] = metric["report_uuid"]
            post(URL(f"{self.server_url}/measurements"), measurement)

    def skip(self, metric_uuid: str, metric) -> bool:
        """Return whether the metric needs to be measured."""
        if self.last_parameters.get(metric_uuid) != metric:
            return False  # Don't skip if metric parameters changed
        return self.next_fetch.get(metric_uuid, datetime.min) > datetime.now()


def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(logging.INFO)
    MetricsCollector().start()


if __name__ == "__main__":
    collect() # pragma: nocover
