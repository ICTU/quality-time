"""Gatling JSON tests collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector, TransactionEntity
from collector_utilities.type import JSONDict
from model import SourceMeasurement, SourceResponses


class GatlingJSONTests(JSONFileSourceCollector):
    """Collector for the number of (successful and/or failing) performance test transactions."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the transactions from the responses and return the transactions with the desired status."""
        transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        counts = dict(failed=0, success=0)
        for response in responses:
            json = await response.json(content_type=None)
            transactions = [transaction["stats"] for transaction in cast(JSONDict, json).get("contents", {}).values()]
            for transaction in transactions:
                entity = TransactionEntity(name=transaction["name"], key=transaction["name"])
                if entity.is_to_be_included(transactions_to_include, transactions_to_ignore):
                    sample_count = transaction["numberOfRequests"]["total"]
                    error_count = transaction["numberOfRequests"]["ko"]
                    counts["success"] += sample_count - error_count
                    counts["failed"] += error_count
        value = sum(counts[status] for status in self._parameter("test_result"))
        return SourceMeasurement(value=str(value), total=str(sum(counts.values())))
