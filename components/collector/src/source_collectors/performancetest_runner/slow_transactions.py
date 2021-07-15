"""Performancetest-runner slow transactions collector."""

from bs4 import Tag

from collector_utilities.functions import match_string_or_regular_expression
from model import Entities, Entity, SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerSlowTransactions(PerformanceTestRunnerBaseClass):
    """Collector for the number of slow transactions in a Performancetest-runner performance test report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the slow transactions from the responses."""
        return Entities([self.__entity(transaction) for transaction in await self.__slow_transactions(responses)])

    @classmethod
    def __entity(cls, transaction) -> Entity:
        """Transform a transaction into a transaction entity."""
        name = cls._name(transaction)
        threshold = "high" if transaction.select("td.red.evaluated") else "warning"
        return Entity(key=name, name=name, threshold=threshold)

    async def __slow_transactions(self, responses: SourceResponses) -> list[Tag]:
        """Return the slow transactions in the performance test report."""
        thresholds = self._parameter("thresholds")
        transactions_to_include = self._parameter("transactions_to_include")
        transactions_to_ignore = self._parameter("transactions_to_ignore")

        def include(transaction) -> bool:
            """Return whether the transaction should be included."""
            name = self._name(transaction)
            if transactions_to_include and not match_string_or_regular_expression(name, transactions_to_include):
                return False
            return not match_string_or_regular_expression(name, transactions_to_ignore)

        slow_transactions: list[Tag] = []
        for response in responses:
            soup = await self._soup(response)
            for color in thresholds:
                slow_transactions.extend(soup.select(f"tr.transaction:has(> td.{color}.evaluated)"))
        return [transaction for transaction in slow_transactions if include(transaction)]
