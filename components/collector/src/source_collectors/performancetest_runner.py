"""Performancetest-runner collector."""

from datetime import datetime
from typing import List

from bs4 import BeautifulSoup, Tag
import requests

from ..source_collector import SourceCollector
from ..type import Entities, Entity, Value
from ..util import days_ago


class PerformanceTestRunnerSlowTransactions(SourceCollector):
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


class PerformanceTestRunnerSourceUpToDateness(SourceCollector):
    """Collector for the performancetest report age."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        datetime_parts = [int(part) for part in soup.find(id="start_of_the_test").string.split(".")]
        test_datetime = datetime(*datetime_parts)  # type: ignore
        return str(days_ago(test_datetime))


class PerformanceTestRunnerPerformanceTestDuration(SourceCollector):
    """Collector for the performancetest duration."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        hours, minutes, seconds = [int(part) for part in soup.find(id="duration").string.split(":", 2)]
        return str(60 * hours + minutes + round(seconds / 60.))


class PerformanceTestRunnerPerformanceTestStability(SourceCollector):
    """Collector for the performancetest stability."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return BeautifulSoup(responses[0].text, "html.parser").find(id="trendbreak_stability").string


class PerformanceTestRunnerTests(SourceCollector):
    """Collector for the number of executed performance test transactions."""

    def statuses_to_count(self) -> List[str]:  # pylint: disable=no-self-use
        """Return the transaction statuses to count."""
        return ["canceled", "failed", "success"]

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        return str(sum(int(soup.find(id=status).string) for status in self.statuses_to_count()))


class PerformanceTestRunnerFailedTests(PerformanceTestRunnerTests):
    """Collector for the number of failed performance test transactions."""

    def statuses_to_count(self):
        return self.parameters.get("failure_type", []) or ["canceled", "failed"]


class PerformanceTestRunnerScalability(SourceCollector):
    """Collector for the scalability metric."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        breaking_point = BeautifulSoup(responses[0].text, "html.parser").find(id="trendbreak_rampup").string
        if breaking_point == "100":
            raise AssertionError("No performance breaking point occurred (breaking point is at 100%, expected < 100%)")
        return breaking_point
