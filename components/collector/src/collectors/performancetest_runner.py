"""Performancetest-runner collector."""

from datetime import datetime
from typing import List

from bs4 import BeautifulSoup, Tag
import requests

from ..collector import Collector
from ..type import Entities, Entity, Value
from ..util import days_ago


class PerformanceTestRunnerSlowTransactions(Collector):
    """Collector for the number of slow transactions in a Performancetest-runner performancetest report."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self.slow_transactions(responses)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:

        def entity(transaction) -> Entity:
            """Transform a transaction into a transaction entity."""
            name = transaction.find("td", class_="name").string
            threshold = "high" if transaction.select("td.red.evaluated") else "warning"
            return dict(key=name, name=name, threshold=threshold)

        return [entity(transaction) for transaction in self.slow_transactions(responses)]

    def slow_transactions(self, responses: List[requests.Response]) -> List[Tag]:
        """Return the slow transactions in the performancetest report."""
        thresholds = self.parameters.get("thresholds") or ["high", "warning"]
        threshold_colors = map(dict(high="red", warning="yellow").get, thresholds)
        soup = BeautifulSoup(responses[0].text, "html.parser")
        slow_transactions: List[Tag] = []
        for color in threshold_colors:
            slow_transactions.extend(soup.select(f"tr.transaction:has(> td.{color}.evaluated)"))
        return slow_transactions


class PerformanceTestRunnerSourceUpToDateness(Collector):
    """Collector for the performancetest report age."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        test_datetime = datetime(*[int(part) for part in soup.find(id="start_of_the_test").string.split(".")])
        return str(days_ago(test_datetime))
