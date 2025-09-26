"""Gatling tests collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import TransactionEntity
from model import SourceMeasurement, SourceResponses

from .base import GatlingHTMLCollector

if TYPE_CHECKING:
    from bs4 import Tag


class GatlingTests(GatlingHTMLCollector):
    """Collector for the number of (successful and/or failing) performance test transactions."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        counts = {"failed": 0, "success": 0}
        for response in responses:
            soup = await self._soup(response)
            if not (table := cast("Tag", soup.find(id="container_statistics_body"))):
                continue
            for row in cast("list[Tag]", table.find_all("tr")):
                name = self.get_column(row, "col-1")
                sample_count = int(self.get_column(row, "col-2"))
                error_count_str = self.get_column(row, "col-4")
                error_count = 0 if error_count_str == "-" else int(error_count_str)
                entity = TransactionEntity(name=name, key=name)
                if not entity.is_to_be_included(transactions_to_include, transactions_to_ignore):
                    continue
                counts["success"] += sample_count - error_count
                counts["failed"] += error_count
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))
