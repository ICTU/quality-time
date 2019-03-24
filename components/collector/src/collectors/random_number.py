"""Metric collector that returns random values."""

import io
import random

import requests

from ..collector import Collector
from ..type import URL


class Random(Collector):
    """Random number metric collector."""
    min = 0
    max = 50

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Return a random number as the response."""
        response = requests.Response()
        response.raw = io.BytesIO(bytes(str(random.randint(self.min, self.max)), "utf-8"))
        response.status_code = requests.status_codes.codes["OK"]
        return response


class RandomDuplicatedLines(Random):
    """Random number of duplicated lines."""


class RandomUncoveredLines(Random):
    """Random number of uncovered lines."""


class RandomUncoveredBranches(Random):
    """Random number of uncovered branches."""


class RandomJobs(Random):
    """Random number of jobs."""


class RandomFailedJobs(Random):
    """Random number of failed jobs."""


class RandomIssues(Random):
    """Random number of issues."""


class RandomLOC(Random):
    """Random number of lines of code."""


class RandomNCLOC(Random):
    """Random number of non-commented lines of code."""


class RandomTests(Random):
    """Random number of tests."""


class RandomFailedTests(Random):
    """Random number of failed tests."""


class RandomUnusedJobs(Random):
    """Random number of failed tests."""


class RandomViolations(Random):
    """Random number of violations."""
