"""Measurement collector."""

import logging
import os
import urllib.parse
from time import sleep
from typing import cast, Dict, Type

import requests

from .collectors import *  # Make sure subclasses are registered
from .collector import Collector
from .type import Report, Response, URL


def fetch_report(server: URL) -> Report:
    """Fetch the report configuration."""
    logging.info("Retrieving report")
    try:
        return requests.get(f"{server}/report").json()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Couldn't retrieve report: %s", reason)
        return dict(subjects=[])


def fetch_and_post_measurement(server: URL, metric_uuid: str, metric) -> None:
    """Fetch and store one measurement."""
    measurement = Collector(metric).get()
    try:
        logging.info(requests.post(f"{server}/measurement/{metric_uuid}", json=measurement))
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Posting measurement for %s (%s) failed: %s", metric, metric_uuid, reason)


def fetch_report_and_measurements(server: URL) -> None:
    """Fetch the report and its measurements."""
    report_config_json = fetch_report(server)
    for subject in report_config_json.get("subjects", {}).values():
        for metric_uuid, metric in subject.get("metrics", {}).items():
            fetch_and_post_measurement(server, metric_uuid, metric)


def collect() -> None:
    """Update the reports."""
    logging.getLogger().setLevel(logging.INFO)

    while True:
        logging.info("Collecting...")
        fetch_report_and_measurements(URL(os.environ.get("SERVER_URL", "http://localhost:8080")))
        logging.info("Sleeping...")
        sleep(30)


if __name__ == "__main__":
    collect()
