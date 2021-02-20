"""Performancetest-runner base classes."""

from abc import ABC

from bs4 import BeautifulSoup, Tag

from base_collectors import HTMLFileSourceCollector
from collector_utilities.type import Response


class PerformanceTestRunnerBaseClass(HTMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for performance test runner collectors."""

    @staticmethod
    async def _soup(response: Response):
        """Return the HTML soup."""
        return BeautifulSoup(await response.text(), "html.parser")

    @staticmethod
    def _name(transaction) -> str:
        """Return the name of the transaction."""
        return str(transaction.find("td", class_="name").string)
