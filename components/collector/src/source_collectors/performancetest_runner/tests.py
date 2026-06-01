"""Performancetest-runner tests collector."""

from typing import TYPE_CHECKING, ClassVar, cast

from bs4 import Tag

from model import SourceMeasurement, SourceResponses

from .base import PerformanceTestRunnerBaseClass

if TYPE_CHECKING:
    from collector_utilities.type import Response


class PerformanceTestRunnerTests(PerformanceTestRunnerBaseClass):
    """Collector for the number of (successful and/or failing) performance test transactions."""

    # For each tests status, the column in the HTML table that contains the number of tests with that status:
    COLUMN_INDICES: ClassVar[dict[str, int]] = {"failed": 7, "success": 1}

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        counts = {"failed": 0, "success": 0}
        for response in responses:
            count = await self.__parse_response(response)
            for status in count:
                counts[status] += count[status]
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))

    async def __parse_response(self, response: Response) -> dict[str, int]:
        """Parse the transactions from the response."""
        soup = await self._soup(response)
        count = {"failed": 0, "success": 0}
        for transaction in cast(Tag, soup.find(id="responsetimestable_begin")).select("tr.transaction"):
            if self._matches_filter(self._name(transaction), "transactions_to_include", "transactions_to_ignore"):
                columns = transaction.find_all("td")
                for status, column_index in self.COLUMN_INDICES.items():
                    nr_tests = int(columns[column_index].string or 0)
                    count[status] += nr_tests
        return count
