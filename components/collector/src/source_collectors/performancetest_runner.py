"""Performancetest-runner collector."""

from abc import ABC
from datetime import datetime
from typing import List, Tuple

from bs4 import BeautifulSoup, Tag

from collector_utilities.type import Entities, Entity, Response, Responses, Value
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class PerformanceTestRunnerBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for performancetest runner collectors."""

    file_extensions = ["html"]

    @staticmethod
    def _soup(response: Response):
        """Return the HTML soup."""
        return BeautifulSoup(response.text, "html.parser")


class PerformanceTestRunnerSlowTransactions(PerformanceTestRunnerBaseClass):
    """Collector for the number of slow transactions in a Performancetest-runner performancetest report."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = [self.__entity(transaction) for transaction in self.__slow_transactions(responses)]
        return str(len(entities)), "100", entities

    @staticmethod
    def __entity(transaction) -> Entity:
        """Transform a transaction into a transaction entity."""
        name = transaction.find("td", class_="name").string
        threshold = "high" if transaction.select("td.red.evaluated") else "warning"
        return dict(key=name, name=name, threshold=threshold)

    def __slow_transactions(self, responses: Responses) -> List[Tag]:
        """Return the slow transactions in the performancetest report."""
        thresholds = self._parameter("thresholds")
        slow_transactions: List[Tag] = []
        for response in responses:
            soup = self._soup(response)
            for color in thresholds:
                slow_transactions.extend(soup.select(f"tr.transaction:has(> td.{color}.evaluated)"))
        return slow_transactions


class PerformanceTestRunnerSourceUpToDateness(PerformanceTestRunnerBaseClass, SourceUpToDatenessCollector):
    """Collector for the performancetest report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        datetime_parts = [int(part) for part in self._soup(response).find(id="start_of_the_test").string.split(".")]
        return datetime(*datetime_parts)  # type: ignore


class PerformanceTestRunnerPerformanceTestDuration(PerformanceTestRunnerBaseClass):
    """Collector for the performancetest duration."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        durations = []
        for response in responses:
            hours, minutes, seconds = [
                int(part) for part in self._soup(response).find(id="duration").string.split(":", 2)]
            durations.append(60 * hours + minutes + round(seconds / 60.))
        return str(sum(durations)), "100", []


class PerformanceTestRunnerPerformanceTestStability(PerformanceTestRunnerBaseClass):
    """Collector for the performancetest stability."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        trend_breaks = []
        for response in responses:
            trend_breaks.append(int(self._soup(response).find(id="trendbreak_stability").string))
        return str(min(trend_breaks)), "100", []


class PerformanceTestRunnerTests(PerformanceTestRunnerBaseClass):
    """Collector for the number of performance test transactions."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        count = 0
        statuses = self._parameter("test_result")
        for response in responses:
            count += sum(int(self._soup(response).find(id=status).string) for status in statuses)
        return str(count), "100", []


class PerformanceTestRunnerScalability(PerformanceTestRunnerBaseClass):
    """Collector for the scalability metric."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        trend_breaks = []
        for response in responses:
            breaking_point = int(self._soup(response).find(id="trendbreak_scalability").string)
            if breaking_point == 100:
                raise AssertionError(
                    "No performance scalability breaking point occurred (breaking point is at 100%, expected < 100%)")
            trend_breaks.append(breaking_point)
        return str(min(trend_breaks)), "100", []
