"""Measurement collector."""

import logging
import os
import urllib.parse
from time import sleep
from typing import cast, Dict, Type

import requests

from .metrics import *  # Make sure subclasses are registered
from .sources import *  # Make sure subclasses are registered
from .metric import Metric
from .source import Source
from .type import Report, Response


def get_metric_from_source(request_url: URL) -> Response:
    """Get the metric from the source."""
    url_parts = urllib.parse.urlsplit(request_url)
    metric_name, source_name = url_parts.path.strip("/").split("/", 1)
    query = urllib.parse.parse_qs(url_parts.query)
    metric = cast(Type[Metric], Metric.subclass_for_api(metric_name))(query)
    source = cast(Type[Source], Source.subclass_for_api(f"{source_name}_{metric_name}"))(query)
    urls = query.get("url", [])
    components = query.get("component", [])
    request = dict(request=dict(
        request_url=request_url, metric=metric_name, source=source_name,
        urls=urls, components=components))
    return metric.get(source.get(request))


def fetch_report(server: URL) -> Report:
    """Fetch the report configuration."""
    logging.info("Retrieving report")
    try:
        return requests.get(f"{server}/report").json()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Couldn't retrieve report: %s", reason)
        return dict(subjects=[])


def fetch_and_post_measurement(server: URL, api: URL) -> None:
    """Fetch and store one measurement."""
    measurement = get_metric_from_source(api)
    try:
        logging.info(requests.post(f"{server}/measurement", json=measurement))
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Posting measurement for %s failed: %s", api, reason)


def fetch_report_and_measurements(server: URL) -> None:
    """Fetch the report and its measurements."""
    report_config_json = fetch_report(server)
    for subject in report_config_json["subjects"]:
        for metric in subject["metrics"]:
            fetch_and_post_measurement(server, URL(metric))


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
