"""Metric collector that returns random values."""

import io
import random

import requests

from collector.collector import Collector
from collector.type import URL


class Random(Collector):
    """Random number metric collector."""
    name = "Random"

    def get_source_response(self, url: URL) -> requests.Response:
        """Return a random number as the response."""
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(random.randint(0, 50)), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return response


class RandomCoveredLines(Random):
    """Random number of covered lines."""


class RandomUncoveredLines(Random):
    """Random number of uncovered lines."""


class RandomCoveredBranches(Random):
    """Random number of covered branches."""


class RandomUncoveredBranches(Random):
    """Random number of uncovered branches."""


class RandomJobs(Random):
    """Random number of jobs."""


class RandomFailedJobs(Random):
    """Random number of failed jobs."""


class RandomLOC(Random):
    """Random number of lines of code."""


class RandomNCLOC(Random):
    """Random number of non-commented lines of code."""


class RandomTests(Random):
    """Random number of tests."""


class RandomFailedTests(Random):
    """Random number of failed tests."""


class RandomViolations(Random):
    """Random number of violations."""
