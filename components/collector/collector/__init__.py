"""Report updater."""

import logging
import time
import urllib.parse
from typing import cast, Type

import requests

from .metrics import *  # Make sure subclasses are registered
from .sources import *  # Make sure subclasses are registered
from .metric import Metric
from .source import Source
from .type import Response


def get_metric_from_source(request_url: str) -> Response:
    """Get the metric from the source."""
    url_parts = urllib.parse.urlsplit(request_url)
    metric_name, source_name = url_parts.path.strip("/").split("/", 1)
    query = urllib.parse.parse_qs(url_parts.query)
    metric = cast(Type[Metric], Metric.subclass_for_api(metric_name))(query)
    source = cast(Type[Source], Source.subclass_for_api(f"{source_name}_{metric_name}"))(query)
    urls = query.get("url", [])
    components = query.get("component", [])
    request = dict(request=dict(
            request_url=request_url, metric=metric_name, source=source_name, urls=urls, components=components))
    return metric.get(source.get(request))


def fetch(api):
    """Fetch one API."""
    logging.info("Retrieving %s", api)
    response = requests.get(f"http://server:8080/{api}")
    return response.json()


def fetch_and_post_measurement(api):
    """Fetch and store one measurement."""
    measurement = get_metric_from_source(api)
    logging.info(requests.post("http://server:8080/measurement", json=measurement))


def fetch_report_and_measurements():
    """Fetch the report and its measurements."""
    report_config_json = fetch("report")
    for subject in report_config_json["subjects"]:
        for metric in subject["metrics"]:
            fetch_and_post_measurement(metric)


def collect():
    """Update the reports."""
    logging.getLogger().setLevel(logging.INFO)

    while True:
        logging.info("Sleeping...")
        time.sleep(30)
        logging.info("Working...")
        fetch_report_and_measurements()


if __name__ == "__main__":
    collect()
