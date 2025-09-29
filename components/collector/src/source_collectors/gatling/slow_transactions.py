"""Gatling slow transactions collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import SlowTransactionsCollector, TransactionEntity
from collector_utilities.functions import decimal_round_half_up
from model import Entities, SourceResponses

from .base import GatlingHTMLCollector

if TYPE_CHECKING:
    from bs4 import Tag


class GatlingSlowTransactions(GatlingHTMLCollector, SlowTransactionsCollector):
    """Collector for the number of slow transactions in a Gatling JSON (stats.json) report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the entities from the responses."""
        entities = Entities()
        for response in responses:
            soup = await self._soup(response)
            if not (table := cast("Tag", soup.find(id="container_statistics_body"))):
                continue
            for row in cast("list[Tag]", table.find_all("tr")):
                name = self.get_column(row, "col-1")
                sample_count = int(self.get_column(row, "col-2"))
                error_count_str = self.get_column(row, "col-4")
                error_count = 0 if error_count_str == "-" else int(error_count_str)
                entity = TransactionEntity(
                    key=name,
                    name=name,
                    sample_count=str(sample_count),
                    error_count=str(error_count),
                    error_percentage=str(decimal_round_half_up((float(error_count) / float(sample_count)) * 100)),
                    min_response_time=self.get_column(row, "col-7"),
                    percentile_50_response_time=self.get_column(row, "col-8"),
                    percentile_75_response_time=self.get_column(row, "col-9"),
                    percentile_95_response_time=self.get_column(row, "col-10"),
                    percentile_99_response_time=self.get_column(row, "col-11"),
                    max_response_time=self.get_column(row, "col-12"),
                    mean_response_time=self.get_column(row, "col-13"),
                )
                if self._is_to_be_included_and_is_slow(entity):
                    entities.append(entity)
        return entities
