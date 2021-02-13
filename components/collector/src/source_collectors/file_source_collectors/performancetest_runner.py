"""Performancetest-runner collector."""

from abc import ABC
from datetime import datetime
from typing import Dict, List, cast

from bs4 import BeautifulSoup, Tag

from base_collectors import HTMLFileSourceCollector, SourceCollectorException, SourceUpToDatenessCollector
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import Response
from source_model import Entity, SourceMeasurement, SourceResponses


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


class PerformanceTestRunnerSlowTransactions(PerformanceTestRunnerBaseClass):
    """Collector for the number of slow transactions in a Performancetest-runner performance test report."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the slow transactions from the responses."""
        entities = [self.__entity(transaction) for transaction in await self.__slow_transactions(responses)]
        return SourceMeasurement(entities=entities)

    @classmethod
    def __entity(cls, transaction) -> Entity:
        """Transform a transaction into a transaction entity."""
        name = cls._name(transaction)
        threshold = "high" if transaction.select("td.red.evaluated") else "warning"
        return Entity(key=name, name=name, threshold=threshold)

    async def __slow_transactions(self, responses: SourceResponses) -> List[Tag]:
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

        slow_transactions: List[Tag] = []
        for response in responses:
            soup = await self._soup(response)
            for color in thresholds:
                slow_transactions.extend(soup.select(f"tr.transaction:has(> td.{color}.evaluated)"))
        return [transaction for transaction in slow_transactions if include(transaction)]


class PerformanceTestRunnerSourceUpToDateness(PerformanceTestRunnerBaseClass, SourceUpToDatenessCollector):
    """Collector for the performance test report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the start date time of the test from the response."""
        datetime_parts = [
            int(part) for part in (await self._soup(response)).find(id="start_of_the_test").string.split(".")
        ]
        return datetime(*datetime_parts)  # type: ignore


class PerformanceTestRunnerPerformanceTestDuration(PerformanceTestRunnerBaseClass):
    """Collector for the performance test duration."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the performance test durations from the responses and return the sum in minutes."""
        durations = []
        for response in responses:
            hours, minutes, seconds = [
                int(part) for part in (await self._soup(response)).find(id="duration").string.split(":", 2)
            ]
            durations.append(60 * hours + minutes + round(seconds / 60.0))
        return SourceMeasurement(value=str(sum(durations)))


class PerformanceTestRunnerPerformanceTestStability(PerformanceTestRunnerBaseClass):
    """Collector for the performance test stability."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the trend break percentage from the responses and return the minimum percentage."""
        trend_breaks = []
        for response in responses:
            trend_breaks.append(int((await self._soup(response)).find(id="trendbreak_stability").string))
        return SourceMeasurement(value=str(min(trend_breaks)))


class PerformanceTestRunnerTests(PerformanceTestRunnerBaseClass):
    """Collector for the number of performance test transactions."""

    COLUMN_INDICES = dict(failed=7, success=1)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        transactions_to_include = cast(List[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(List[str], self._parameter("transactions_to_ignore"))
        counts = dict(failed=0, success=0)
        for response in responses:
            count = await self.__parse_response(response, transactions_to_include, transactions_to_ignore)
            for status in count:
                counts[status] += count[status]
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))

    @classmethod
    async def __parse_response(
        cls, response: Response, transactions_to_include: List[str], transactions_to_ignore: List[str]
    ) -> Dict[str, int]:
        """Parse the transactions from the response."""
        soup = await cls._soup(response)
        count = dict(failed=0, success=0)
        for transaction in soup.find(id="responsetimestable_begin").select("tr.transaction"):
            name = cls._name(transaction)
            if transactions_to_include and not match_string_or_regular_expression(name, transactions_to_include):
                continue
            if match_string_or_regular_expression(name, transactions_to_ignore):
                continue
            columns = transaction.find_all("td")
            for status, column_index in cls.COLUMN_INDICES.items():
                nr_tests = int(columns[column_index].string or 0)
                count[status] += nr_tests
        return count


class PerformanceTestRunnerScalability(PerformanceTestRunnerBaseClass):
    """Collector for the scalability metric."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the scalability breaking point from the responses."""
        trend_breaks = []
        for response in responses:
            breaking_point = int((await self._soup(response)).find(id="trendbreak_scalability").string)
            if breaking_point == 100:
                raise SourceCollectorException(
                    "No performance scalability breaking point occurred (breaking point is at 100%, expected < 100%)"
                )
            trend_breaks.append(breaking_point)
        return SourceMeasurement(value=str(min(trend_breaks)))
