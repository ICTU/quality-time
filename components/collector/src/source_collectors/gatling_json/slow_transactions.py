"""Gatling JSON slow transactions collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector, SlowTransactionsCollector, TransactionEntity
from collector_utilities.type import JSON, JSONDict
from model import Entities


class GatlingJSONSlowTransactions(JSONFileSourceCollector, SlowTransactionsCollector):
    """Collector for the number of slow transactions in a Gatling JSON (stats.json) report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the transactions from the JSON."""
        entities = Entities()
        transactions = [transaction["stats"] for transaction in cast(JSONDict, json).get("contents", {}).values()]
        for transaction in transactions:
            sample_count = transaction["numberOfRequests"]["total"]
            error_count = transaction["numberOfRequests"]["ko"]
            entity = TransactionEntity(
                key=transaction["name"],
                name=transaction["name"],
                sample_count=sample_count,
                error_count=error_count,
                error_percentage=self._round((float(error_count) / float(sample_count)) * 100),
                mean_response_time=self._round(transaction["meanResponseTime"]["total"]),
                min_response_time=self._round(transaction["minResponseTime"]["total"]),
                max_response_time=self._round(transaction["maxResponseTime"]["total"]),
                percentile_50_response_time=self._round(transaction["percentiles1"]["total"]),
                percentile_75_response_time=self._round(transaction["percentiles2"]["total"]),
                percentile_95_response_time=self._round(transaction["percentiles3"]["total"]),
                percentile_99_response_time=self._round(transaction["percentiles4"]["total"]),
            )
            if self._is_to_be_included_and_is_slow(entity):
                entities.append(entity)
        return entities
