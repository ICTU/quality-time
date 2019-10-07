"""Performancetest-runner collector."""

from datetime import datetime
from typing import List

from bs4 import BeautifulSoup, Tag

from utilities.type import Entities, Entity, Responses, Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class PerformanceTestRunnerSlowTransactions(SourceCollector):
    """Collector for the number of slow transactions in a Performancetest-runner performancetest report."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self.__slow_transactions(responses)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:

        def entity(transaction) -> Entity:
            """Transform a transaction into a transaction entity."""
            name = transaction.find("td", class_="name").string
            threshold = "high" if transaction.select("td.red.evaluated") else "warning"
            return dict(key=name, name=name, threshold=threshold)

        return [entity(transaction) for transaction in self.__slow_transactions(responses)]

    def __slow_transactions(self, responses: Responses) -> List[Tag]:
        """Return the slow transactions in the performancetest report."""
        thresholds = self._parameter("thresholds")
        soup = BeautifulSoup(responses[0].text, "html.parser")
        slow_transactions: List[Tag] = []
        for color in thresholds:
            slow_transactions.extend(soup.select(f"tr.transaction:has(> td.{color}.evaluated)"))
        return slow_transactions


class PerformanceTestRunnerSourceUpToDateness(SourceCollector):
    """Collector for the performancetest report age."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        datetime_parts = [int(part) for part in soup.find(id="start_of_the_test").string.split(".")]
        test_datetime = datetime(*datetime_parts)  # type: ignore
        return str(days_ago(test_datetime))


class PerformanceTestRunnerPerformanceTestDuration(SourceCollector):
    """Collector for the performancetest duration."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        hours, minutes, seconds = [int(part) for part in soup.find(id="duration").string.split(":", 2)]
        return str(60 * hours + minutes + round(seconds / 60.))


class PerformanceTestRunnerPerformanceTestStability(SourceCollector):
    """Collector for the performancetest stability."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(BeautifulSoup(responses[0].text, "html.parser").find(id="trendbreak_stability").string)


class PerformanceTestRunnerTests(SourceCollector):
    """Collector for the number of performance test transactions."""

    status_parameter = "test_result"

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        soup = BeautifulSoup(responses[0].text, "html.parser")
        return str(sum(int(soup.find(id=status).string) for status in self._parameter(self.status_parameter)))


class PerformanceTestRunnerFailedTests(PerformanceTestRunnerTests):
    """Collector for the number of failed performance test transactions."""

    status_parameter = "failure_type"


class PerformanceTestRunnerScalability(SourceCollector):
    """Collector for the scalability metric."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        breaking_point = str(BeautifulSoup(responses[0].text, "html.parser").find(id="trendbreak_scalability").string)
        if breaking_point == "100":
            raise AssertionError(
                "No performance scalability breaking point occurred (breaking point is at 100%, expected < 100%)")
        return breaking_point
