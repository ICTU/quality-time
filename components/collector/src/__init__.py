"""Measurement collector."""

import logging
from typing import NoReturn

# Make sure subclasses are registered
from .source_collectors import *  # pylint: disable=unused-wildcard-import,wildcard-import
from .metrics_collector import MetricsCollector


def collect() -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(logging.INFO)
    MetricsCollector().start()


if __name__ == "__main__":
    collect() # pragma: nocover
