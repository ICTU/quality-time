"""Performancetest-runner base classes."""

from abc import ABC

from base_collectors import HTMLFileSourceCollector
from collector_utilities.type import Response


class PerformanceTestRunnerBaseClass(HTMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for performance test runner collectors."""

    @staticmethod
    def _name(transaction) -> str:
        """Return the name of the transaction."""
        return str(transaction.find("td", class_="name").string)
