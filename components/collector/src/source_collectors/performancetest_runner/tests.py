"""Performancetest-runner tests collector."""

from typing import cast

from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import Response
from source_model import SourceMeasurement, SourceResponses

from .base import PerformanceTestRunnerBaseClass


class PerformanceTestRunnerTests(PerformanceTestRunnerBaseClass):
    """Collector for the number of performance test transactions."""

    COLUMN_INDICES = dict(failed=7, success=1)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        counts = dict(failed=0, success=0)
        for response in responses:
            count = await self.__parse_response(response, transactions_to_include, transactions_to_ignore)
            for status in count:
                counts[status] += count[status]
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))

    @classmethod
    async def __parse_response(
        cls, response: Response, transactions_to_include: list[str], transactions_to_ignore: list[str]
    ) -> dict[str, int]:
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
