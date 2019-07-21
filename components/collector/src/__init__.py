"""Measurement collector."""

import logging
from typing import NoReturn

from .metric_collectors import MetricsCollector
# Make sure subclasses are registered
from .source_collectors import *  # pylint: disable=unused-wildcard-import,wildcard-import


def collect(loglevel=None) -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(loglevel or logging.ERROR)
    MetricsCollector().start()


if __name__ == "__main__":
    collect(logging.INFO) # pragma: nocover
