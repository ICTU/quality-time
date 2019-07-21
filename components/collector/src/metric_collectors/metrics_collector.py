"""Metrics collector."""

from datetime import datetime
import logging
import os
import time
from typing import Any, Dict, NoReturn

import requests

from .metric_collector import MetricCollector
from ..utilities.type import URL


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
        self.server_url = URL(os.environ.get("SERVER_URL", "http://localhost:5001"))
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
        datamodel = get(URL(f"{self.server_url}/datamodel"))
        metrics = get(URL(f"{self.server_url}/metrics"))
        for metric_uuid, metric in metrics.items():
            collector = MetricCollector(metric, datamodel)
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
