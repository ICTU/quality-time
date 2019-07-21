"""Measurement collector."""

import logging
from typing import NoReturn

from metric_collectors import MetricsCollector
# Make sure subclasses are registered
from source_collectors import *  # pylint: disable=unused-wildcard-import,wildcard-import


def collect(log_level: int = None) -> NoReturn:
    """Collect the measurements indefinitely."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    MetricsCollector().start()


if __name__ == "__main__":
    collect(logging.INFO)  # pragma: nocover
